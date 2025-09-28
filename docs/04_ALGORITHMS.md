# Fall Detection Algorithms

## Algorithm Evolution

The system has evolved through three major algorithmic phases, each improving accuracy and predictive capabilities.

### Phase 1: Threshold-Based Detection
- Simple gyroscope magnitude threshold
- Binary classification (fall/no-fall)
- ~70% accuracy

### Phase 2: Multi-Sensor Fusion
- Combined gyroscope and accelerometer
- Weighted voting system
- ~80% accuracy

### Phase 3: Mathematical Model (Current)
- Quaternion-based orientation tracking
- Human Body Kinematics (HBK) model
- Logistic regression prediction
- **88% accuracy**

## Current Algorithm Implementation

### Overview

The current system implements the mathematical model from Mohammed et al. (2024), combining:
1. Quaternion-based orientation tracking
2. Three-joint kinematic model
3. Logistic regression for fall prediction
4. Two-phase detection system

## Quaternion Mathematics

### Quaternion Representation

A quaternion q represents 3D rotation as a 4D vector:

```
q = [q0, q1, q2, q3] = [w, x, y, z]
```

Where:
- `q0` (w): Scalar component
- `q1, q2, q3` (x, y, z): Vector components
- Constraint: |q| = 1 (unit quaternion)

### Quaternion from Axis-Angle

Given rotation axis **u** and angle θ:

```
q = [cos(θ/2), u·sin(θ/2)]
```

### Quaternion Operations

**Multiplication** (composition of rotations):
```python
def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    
    return [w, x, y, z]
```

**Conjugate** (inverse rotation):
```python
def quaternion_conjugate(q):
    return [q[0], -q[1], -q[2], -q[3]]
```

### Integration from Gyroscope Data

Convert angular velocity to quaternion update:

```python
def gyro_to_quaternion(wx, wy, wz, dt):
    # Magnitude of rotation
    angle = np.sqrt(wx**2 + wy**2 + wz**2) * dt
    
    if angle > 0:
        # Normalized axis
        axis = [wx/angle, wy/angle, wz/angle]
        
        # Create quaternion
        q = [
            np.cos(angle/2),
            axis[0] * np.sin(angle/2),
            axis[1] * np.sin(angle/2),
            axis[2] * np.sin(angle/2)
        ]
    else:
        q = [1, 0, 0, 0]  # No rotation
    
    return q
```

## Human Body Kinematics Model

### Joint Hierarchy

The model tracks three primary joints:

```
World Frame
    │
    └── Hip (Reference)
         ├── Thoracic (Upper body)
         └── Knee (Lower body)
```

### Coordinate Systems

**T-Pose Reference**:
- X-axis: Forward
- Y-axis: Up (along spine)
- Z-axis: Right

### Joint Angle Calculation

Calculate relative angles between joints:

```python
def calculate_joint_angle(q_joint, q_reference):
    """
    Calculate angle between joint and reference
    
    Args:
        q_joint: Joint quaternion [q0, q1, q2, q3]
        q_reference: Reference quaternion (hip)
    
    Returns:
        angle: Joint angle in radians
    """
    # Relative quaternion
    q_rel = quaternion_multiply(
        q_joint, 
        quaternion_conjugate(q_reference)
    )
    
    # Extract angle from quaternion
    angle = 2 * np.arccos(np.clip(q_rel[0], -1.0, 1.0))
    
    return angle
```

### Three-Joint Model Implementation

```python
class HumanBodyKinematics:
    def __init__(self):
        self.q_thoracic = [1, 0, 0, 0]
        self.q_hip = [1, 0, 0, 0]
        self.q_knee = [1, 0, 0, 0]
    
    def update_from_sensors(self, sensor_data):
        """Update joint quaternions from sensor data"""
        for sensor in sensor_data:
            if sensor['id'] == 1:  # Thoracic
                self.q_thoracic = self.integrate_gyro(
                    sensor['gx'], sensor['gy'], sensor['gz']
                )
            elif sensor['id'] == 2:  # Hip
                self.q_hip = self.integrate_gyro(
                    sensor['gx'], sensor['gy'], sensor['gz']
                )
            elif sensor['id'] == 3:  # Knee
                self.q_knee = self.integrate_gyro(
                    sensor['gx'], sensor['gy'], sensor['gz']
                )
    
    def get_joint_angles(self):
        """Calculate all joint angles relative to hip"""
        thoracic_angle = calculate_joint_angle(
            self.q_thoracic, self.q_hip
        )
        knee_angle = calculate_joint_angle(
            self.q_knee, self.q_hip
        )
        
        return thoracic_angle, knee_angle
```

## Logistic Regression Model

### Mathematical Foundation

The fall probability is calculated using logistic regression:

```
P(fall) = 1 / (1 + e^(-z))

where z = β₀ + β₁x₁ + β₂x₂ + β₃x₃
```

Variables:
- `x₁`: Thoracic angle
- `x₂`: Hip angle  
- `x₃`: Knee angle
- `β₀, β₁, β₂, β₃`: Model coefficients

### Trained Coefficients

Based on IEEE paper validation:

| Parameter | Value | Std Error | Significance |
|-----------|-------|-----------|--------------|
| β₀ (Intercept) | -2.834 | 0.234 | p < 0.001 |
| β₁ (Thoracic) | 0.034 | 0.018 | p = 0.046 |
| β₂ (Hip) | 0.153 | 0.012 | p = 0.028 |
| β₃ (Knee) | 0.193 | 0.027 | p = 0.030 |

### Implementation

```python
class FallPredictor:
    def __init__(self):
        # Trained coefficients
        self.beta_0 = -2.834
        self.beta_1 = 0.034
        self.beta_2 = 0.153
        self.beta_3 = 0.193
        
        # Decision threshold
        self.threshold = 0.85
    
    def predict_probability(self, thoracic_angle, hip_angle, knee_angle):
        """
        Calculate fall probability
        
        Returns:
            probability: Value between 0 and 1
        """
        z = (self.beta_0 + 
             self.beta_1 * thoracic_angle +
             self.beta_2 * hip_angle +
             self.beta_3 * knee_angle)
        
        probability = 1 / (1 + np.exp(-z))
        
        return probability
    
    def classify(self, probability):
        """
        Binary classification based on threshold
        
        Returns:
            'fall' or 'no_fall'
        """
        return 'fall' if probability > self.threshold else 'no_fall'
```

## Two-Phase Detection System

### Phase 1: Prediction (Pre-Impact)

Detect abnormal motion patterns before fall:

```python
def prediction_phase(sensor_data, time_window=0.5):
    """
    Analyze motion patterns for fall prediction
    
    Args:
        sensor_data: Recent sensor readings
        time_window: Analysis window in seconds
    
    Returns:
        risk_level: 'low', 'medium', 'high'
    """
    # Calculate motion features
    features = {
        'angular_velocity': calculate_angular_velocity(sensor_data),
        'acceleration_variance': calculate_variance(sensor_data),
        'jerk': calculate_jerk(sensor_data),
        'orientation_change': calculate_orientation_delta(sensor_data)
    }
    
    # Risk assessment
    if features['angular_velocity'] > 2.0:
        return 'high'
    elif features['angular_velocity'] > 1.0:
        return 'medium'
    else:
        return 'low'
```

### Phase 2: Detection (Impact)

Confirm fall occurrence:

```python
def detection_phase(sensor_data):
    """
    Confirm fall detection
    
    Returns:
        is_fall: Boolean
        confidence: 0-1
    """
    # Multi-sensor voting
    votes = []
    
    for sensor in sensor_data:
        gyro_mag = np.sqrt(
            sensor['gx']**2 + 
            sensor['gy']**2 + 
            sensor['gz']**2
        )
        
        if gyro_mag > FALL_THRESHOLD:
            votes.append(1)
        else:
            votes.append(0)
    
    # Require majority vote
    is_fall = sum(votes) >= 2
    confidence = sum(votes) / len(votes)
    
    return is_fall, confidence
```

## Algorithm Performance Metrics

### Confusion Matrix

Based on IMU dataset validation:

```
              Predicted
           Fall    No Fall
Actual  ┌────────┬────────┐
Fall    │  150   │   21   │  Sensitivity: 87.7%
        ├────────┼────────┤
No Fall │   48   │  181   │  Specificity: 79.0%
        └────────┴────────┘
           PPV: 75.8%  NPV: 89.6%
```

### ROC Curve Analysis

- **AUC**: 0.853 (training), 0.903 (testing)
- **Optimal Threshold**: 0.85
- **F1 Score**: 0.81

## Real-Time Implementation

### Processing Pipeline

```python
class RealtimeFallDetector:
    def __init__(self):
        self.hbk_model = HumanBodyKinematics()
        self.predictor = FallPredictor()
        self.buffer = SensorBuffer(window_size=50)  # 5 seconds at 10Hz
    
    def process_packet(self, packet):
        """Process single UDP packet"""
        # Parse packet
        sensor_data = parse_packet(packet)
        
        # Add to buffer
        self.buffer.add(sensor_data)
        
        # Update kinematics
        self.hbk_model.update_from_sensors([sensor_data])
        
        # Get joint angles
        thoracic, knee = self.hbk_model.get_joint_angles()
        
        # Predict fall probability
        probability = self.predictor.predict_probability(
            thoracic, 0, knee  # Hip angle is 0 (reference)
        )
        
        # Two-phase detection
        if probability > 0.5:  # Warning threshold
            risk = self.prediction_phase(self.buffer.get_window())
            
            if risk == 'high':
                is_fall, confidence = self.detection_phase(
                    self.buffer.get_recent(3)  # Last 300ms
                )
                
                if is_fall:
                    self.trigger_alert(confidence)
        
        return {
            'probability': probability,
            'status': 'fall' if probability > 0.85 else 'normal'
        }
```

## Parameter Tuning

### Adjustable Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `FALL_THRESHOLD` | 4.0 rad/s | 2.0-6.0 | Gyro magnitude for fall |
| `WARNING_THRESHOLD` | 1.5 rad/s | 1.0-3.0 | Pre-fall warning |
| `DECISION_THRESHOLD` | 0.85 | 0.7-0.95 | Logistic regression cutoff |
| `WINDOW_SIZE` | 50 samples | 30-100 | Analysis window |
| `MIN_SENSORS` | 2 | 1-3 | Minimum sensors for detection |

### Population-Specific Tuning

```python
# Elderly (more sensitive)
ELDERLY_CONFIG = {
    'fall_threshold': 3.5,
    'warning_threshold': 1.2,
    'decision_threshold': 0.80
}

# Young Adults (less sensitive)
ADULT_CONFIG = {
    'fall_threshold': 5.0,
    'warning_threshold': 2.0,
    'decision_threshold': 0.90
}

# Clinical Setting (balanced)
CLINICAL_CONFIG = {
    'fall_threshold': 4.0,
    'warning_threshold': 1.5,
    'decision_threshold': 0.85
}
```

## Future Algorithm Enhancements

### Machine Learning Integration

1. **Deep Learning Models**
   - LSTM for temporal patterns
   - CNN for feature extraction
   - Transformer architecture for sequence modeling

2. **Personalized Models**
   - Individual gait patterns
   - Adaptive thresholds
   - Activity recognition

3. **Multi-Modal Fusion**
   - Heart rate variability
   - Blood pressure changes
   - Environmental context

### Advanced Features

- **Fall Direction Prediction**: Classify fall type (forward, backward, lateral)
- **Impact Force Estimation**: Predict injury severity
- **Recovery Detection**: Identify successful balance recovery
- **Activity Classification**: Distinguish ADL from falls

---
*Next: [Raspberry Pi Setup](05_RASPBERRY_PI.md)*
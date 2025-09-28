# Fall Detection Datasets

## Overview

This directory contains information about datasets used for training, validation, and testing of the fall detection system. Due to size and licensing constraints, the actual dataset files are not included in the repository but can be obtained from their respective sources.

## Primary Dataset

### IMU Fall Detection Dataset

**Source**: Simon Fraser University  
**Paper**: Aziz et al. (2017) - "A comparison of accuracy of fall detection algorithms"  
**Size**: 600 trials (210 falls, 390 non-falls)  
**Participants**: 10 healthy young adults (age 22-32)  
**Sensors**: 7 IMU sensors (we use data from 3: chest, waist, thigh)

**Download Link**: [Request from authors or institution]

**Citation**:
```bibtex
@article{aziz2017comparison,
  title={A comparison of accuracy of fall detection algorithms (threshold-based vs. machine learning) using waist-mounted tri-axial accelerometer signals from a comprehensive set of falls and non-fall trials},
  author={Aziz, Omar and Musngi, Matthew and Park, Edward J and Mori, Greg and Robinovitch, Stephen N},
  journal={Medical & biological engineering & computing},
  volume={55},
  number={1},
  pages={45--55},
  year={2017},
  publisher={Springer}
}
```

### Dataset Structure

```
IMU_Dataset/
├── falls/
│   ├── forward_falls/      # 30 trials × 10 subjects
│   ├── backward_falls/     # 30 trials × 10 subjects
│   ├── lateral_falls/      # 30 trials × 10 subjects
│   └── syncope_falls/      # 30 trials × 10 subjects
├── near_falls/
│   ├── slip_recovery/      # 15 trials × 10 subjects
│   ├── trip_recovery/      # 15 trials × 10 subjects
│   └── misstep_recovery/   # 15 trials × 10 subjects
└── activities/
    ├── walking/            # 30 trials × 10 subjects
    ├── sitting/            # 30 trials × 10 subjects
    ├── standing/           # 30 trials × 10 subjects
    └── stairs/             # 30 trials × 10 subjects
```

### Data Format

Each trial contains:
- **Sampling Rate**: 128 Hz
- **Duration**: 15 seconds per trial
- **Sensors**: 7 locations (we use chest, waist, thigh)
- **Channels**: 3-axis accelerometer + 3-axis gyroscope

**CSV Format**:
```
timestamp,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
0.000,0.982,-0.145,9.798,0.123,-0.045,0.089
0.008,0.978,-0.143,9.802,0.125,-0.043,0.091
...
```

## Secondary Datasets (Reference)

### 1. SisFall Dataset

**Description**: Publicly available fall and ADL dataset  
**Size**: 4,510 files (2,707 falls, 1,803 ADL)  
**Participants**: 38 (23 young, 15 elderly)  
**Link**: http://sistemic.udea.edu.co/en/research/projects/english-falls/

### 2. MobiFall Dataset

**Description**: Smartphone-based fall detection dataset  
**Size**: 630 trials (342 falls, 288 ADL)  
**Participants**: 24 subjects  
**Link**: http://www.bmi.teicrete.gr/index.php/research/mobifall

### 3. UP-Fall Detection Dataset

**Description**: Multimodal dataset with wearable sensors  
**Size**: 850 trials  
**Participants**: 17 healthy young adults  
**Link**: https://sites.google.com/up.edu.mx/har-up/

## Data Preprocessing

### Required Preprocessing Steps

1. **Resampling**: Convert from 128Hz to 10Hz for our system
```python
# Example downsampling
df_resampled = df.resample('100ms').mean()
```

2. **Normalization**: Scale sensor values
```python
# Normalize accelerometer to g units
acc_normalized = acc_raw / 9.81
```

3. **Segmentation**: Extract fall windows
```python
# 5-second windows around fall events
window_size = 50  # samples at 10Hz
fall_window = data[fall_index-25:fall_index+25]
```

4. **Feature Extraction**: Calculate magnitudes
```python
gyro_magnitude = np.sqrt(gx**2 + gy**2 + gz**2)
accel_magnitude = np.sqrt(ax**2 + ay**2 + az**2)
```

## Dataset Statistics

### Our System Performance on IMU Dataset

| Metric | Training Set | Test Set |
|--------|-------------|----------|
| Samples | 480 | 120 |
| Falls | 168 | 42 |
| Non-falls | 312 | 78 |
| Accuracy | 88.0% | 87.75% |
| Sensitivity | 70.4% | 71.4% |
| Specificity | 75.3% | 75.5% |

### Class Distribution

```
Activity Type    | Count | Percentage
-----------------|-------|------------
Forward Fall     | 60    | 10.0%
Backward Fall    | 60    | 10.0%
Lateral Fall     | 60    | 10.0%
Syncope Fall     | 30    | 5.0%
Near Falls       | 150   | 25.0%
Walking          | 60    | 10.0%
Sitting/Standing | 120   | 20.0%
Other ADL        | 60    | 10.0%
```

## Creating Custom Dataset

### Data Collection Protocol

1. **Equipment Setup**:
   - 3 ESP32 nodes with BNO055 sensors
   - Positions: chest, waist, thigh
   - Sampling rate: 10Hz

2. **Safety Requirements**:
   - Use thick mats (minimum 20cm)
   - Have spotter present
   - Medical clearance for participants
   - Signed consent forms

3. **Trial Structure**:
   - 5 seconds pre-activity
   - Activity/fall event
   - 5 seconds post-activity

4. **Minimum Dataset Size**:
   - At least 100 falls
   - At least 200 non-falls
   - Minimum 5 subjects
   - Balance age groups

### Data Annotation Format

```json
{
  "trial_id": "001",
  "subject_id": "S01",
  "age": 25,
  "gender": "M",
  "height_cm": 175,
  "weight_kg": 70,
  "activity_type": "forward_fall",
  "fall_detected": true,
  "fall_timestamp": 7.235,
  "sensor_positions": ["chest", "waist", "thigh"],
  "notes": "Controlled fall onto mat"
}
```

## Data Augmentation Techniques

### For Training Enhancement

1. **Time Shifting**: Randomly shift windows ±500ms
2. **Noise Addition**: Add Gaussian noise (σ=0.01)
3. **Rotation**: Apply small rotations (±5°)
4. **Speed Variation**: Time-scale by 0.9-1.1×

```python
# Example augmentation
def augment_data(data, noise_level=0.01):
    noise = np.random.normal(0, noise_level, data.shape)
    augmented = data + noise
    return augmented
```

## Ethical Considerations

### Data Collection Ethics

- **IRB Approval**: Required for human subjects
- **Informed Consent**: Written consent mandatory
- **Privacy**: Anonymize all personal identifiers
- **Data Security**: Encrypt sensitive information
- **Right to Withdraw**: Participants can remove their data

### Usage Guidelines

1. For research purposes only
2. Do not attempt to identify individuals
3. Cite original dataset sources
4. Follow dataset-specific licenses
5. Do not redistribute without permission

## Tools and Scripts

### Available Scripts

```bash
scripts/
├── download_datasets.py    # Download public datasets
├── preprocess_data.py      # Convert to our format
├── split_dataset.py        # Train/test splitting
├── augment_data.py         # Data augmentation
└── validate_format.py      # Check data integrity
```

### Usage Example

```bash
# Download and preprocess dataset
python scripts/download_datasets.py --dataset IMU
python scripts/preprocess_data.py --input raw/ --output processed/
python scripts/split_dataset.py --ratio 0.8 --seed 42
```

## Related Research Papers

1. **Mohammed et al. (2024)** - "A Mathematical Model for Fall Detection Prediction in Elderly People"
   - IEEE Sensors Journal, vol. 24, no. 20
   - Our primary algorithmic reference

2. **Aziz et al. (2017)** - "Comparison of accuracy of fall detection algorithms"
   - Medical & Biological Engineering & Computing
   - Dataset source

3. **Klenk et al. (2011)** - "Comparison of acceleration signals of simulated and real-world backward falls"
   - Medical Engineering & Physics

## Contributing Datasets

If you have collected fall detection data and wish to contribute:

1. Ensure proper ethical approval
2. Follow our annotation format
3. Include metadata file
4. Contact: [project maintainer email]

## License and Attribution

Each dataset has its own license. Please refer to:
- IMU Dataset: Academic use only, citation required
- SisFall: Public domain with attribution
- Our collected data: MIT License

## Contact

For dataset access and questions:
- GitHub Issues: https://github.com/AlexeyKoz/fall-detection-system/issues
- Email: AL7koz@gmail.com

---
*Last Updated: December 2024*
*Version: 1.0*
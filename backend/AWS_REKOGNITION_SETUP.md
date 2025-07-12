# AWS Rekognition Setup Guide

## Issue
The brand asset analyzer uses AWS Rekognition for advanced text detection and brand element recognition. Currently, the AWS user lacks the necessary permissions, resulting in these errors:

```
AccessDeniedException: User: arn:aws:iam::975049977564:user/snapbrand is not authorized to perform: rekognition:DetectText
AccessDeniedException: User: arn:aws:iam::975049977564:user/snapbrand is not authorized to perform: rekognition:DetectLabels
```

## Solution

### Option 1: Add Rekognition Permissions (Recommended)

Add the following IAM policy to the `snapbrand` user:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectText",
                "rekognition:DetectLabels"
            ],
            "Resource": "*"
        }
    ]
}
```

### Option 2: Use AWS Managed Policy

Attach the AWS managed policy `AmazonRekognitionReadOnlyAccess` to the user:

```bash
aws iam attach-user-policy \
    --user-name snapbrand \
    --policy-arn arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess
```

### Option 3: Continue Without Rekognition

The system has been updated to work gracefully without Rekognition. The brand asset analyzer will:

- ✅ Still perform color palette extraction
- ✅ Still analyze visual characteristics (brightness, contrast, style)
- ✅ Still provide composition analysis
- ❌ Skip text detection (will return empty text_elements)
- ❌ Skip brand element detection (will return empty brand_indicators)

## Features Affected

### With Rekognition:
- **Text Detection**: Extracts text from uploaded brand assets
- **Brand Element Detection**: Identifies logos, emblems, symbols in images
- **Enhanced Brand Consistency**: Better validation using detected text and elements

### Without Rekognition:
- **Core Analysis**: Color, style, composition analysis still works
- **Brand Validation**: Uses color and style consistency only
- **Reduced Accuracy**: Some brand consistency checks may be less precise

## Current Status

The system is currently running **without Rekognition** but all core brand intelligence features remain functional. Adding Rekognition permissions will enhance the accuracy of brand analysis but is not required for basic operation.

## Cost Considerations

AWS Rekognition pricing (as of 2024):
- Text Detection: $0.0015 per image
- Label Detection: $0.001 per image

For typical usage (analyzing brand assets), the cost is minimal but should be considered for high-volume applications.
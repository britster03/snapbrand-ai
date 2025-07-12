import io
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import colorsys
from collections import Counter
import boto3
from botocore.exceptions import ClientError
import cv2
import requests
from io import BytesIO

logger = logging.getLogger(__name__)


class BrandAssetAnalyzer:
    """Service for analyzing brand assets and extracting visual attributes."""
    
    def __init__(self, s3_client: boto3.client):
        self.s3_client = s3_client
        try:
            self.rekognition_client = boto3.client('rekognition')
            self.rekognition_available = True
        except Exception as e:
            logger.warning(f"Rekognition client initialization failed: {str(e)}")
            self.rekognition_client = None
            self.rekognition_available = False
        
    def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """Analyze an image and extract brand-relevant attributes."""
        try:
            # Download image
            image = self._download_image(image_url)
            
            # Extract various attributes
            analysis_result = {
                "dominant_colors": self._extract_color_palette(image),
                "style_attributes": self._analyze_style_attributes(image),
                "composition_data": self._analyze_composition(image),
                "text_elements": self._extract_text_elements(image_url),
                "visual_characteristics": self._analyze_visual_characteristics(image),
                "brand_elements": self._detect_brand_elements(image_url)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise
    
    def _download_image(self, image_url: str) -> Image.Image:
        """Download image from URL."""
        if image_url.startswith('s3://'):
            # Handle S3 URLs
            bucket, key = self._parse_s3_url(image_url)
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            image_data = response['Body'].read()
            return Image.open(BytesIO(image_data))
        else:
            # Handle HTTP URLs
            response = requests.get(image_url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
    
    def _parse_s3_url(self, s3_url: str) -> Tuple[str, str]:
        """Parse S3 URL to extract bucket and key."""
        s3_url = s3_url.replace('s3://', '')
        parts = s3_url.split('/', 1)
        return parts[0], parts[1]
    
    def _extract_color_palette(self, image: Image.Image, n_colors: int = 8) -> List[Dict[str, Any]]:
        """Extract dominant colors from image using K-means clustering."""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize for faster processing
        image_small = image.resize((150, 150))
        pixels = np.array(image_small).reshape(-1, 3)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get color centers and their frequencies
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        label_counts = Counter(labels)
        
        # Create color palette with metadata
        palette = []
        for i, color in enumerate(colors):
            rgb = tuple(int(c) for c in color)  # Convert numpy types to Python int
            hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
            hsv = colorsys.rgb_to_hsv(*(c/255 for c in rgb))
            
            palette.append({
                "hex": hex_color,
                "rgb": list(rgb),
                "hsv": {
                    "h": int(hsv[0] * 360),
                    "s": int(hsv[1] * 100),
                    "v": int(hsv[2] * 100)
                },
                "percentage": round(label_counts[i] / len(labels) * 100, 2),
                "name": self._get_color_name(rgb)
            })
        
        # Sort by percentage
        palette.sort(key=lambda x: x['percentage'], reverse=True)
        return palette
    
    def _get_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Get a descriptive name for a color."""
        r, g, b = rgb
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h = h * 360
        s = s * 100
        v = v * 100
        
        # Determine color name based on HSV values
        if v < 20:
            return "black"
        elif v > 95 and s < 5:
            return "white"
        elif s < 10:
            if v < 40:
                return "dark_gray"
            elif v < 70:
                return "gray"
            else:
                return "light_gray"
        elif 0 <= h < 20 or 340 <= h:
            return "red"
        elif 20 <= h < 45:
            return "orange"
        elif 45 <= h < 70:
            return "yellow"
        elif 70 <= h < 150:
            return "green"
        elif 150 <= h < 200:
            return "cyan"
        elif 200 <= h < 260:
            return "blue"
        elif 260 <= h < 290:
            return "purple"
        else:
            return "magenta"
    
    def _analyze_style_attributes(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze visual style attributes of the image."""
        # Convert to numpy array for OpenCV
        img_array = np.array(image)
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Calculate various metrics
        attributes = {
            "contrast": self._calculate_contrast(gray),
            "brightness": self._calculate_brightness(gray),
            "sharpness": self._calculate_sharpness(gray),
            "complexity": self._calculate_visual_complexity(gray),
            "style_descriptors": self._determine_style_descriptors(image, gray)
        }
        
        return attributes
    
    def _calculate_contrast(self, gray_image: np.ndarray) -> float:
        """Calculate image contrast using standard deviation."""
        return float(np.std(gray_image))
    
    def _calculate_brightness(self, gray_image: np.ndarray) -> float:
        """Calculate average brightness."""
        return float(np.mean(gray_image))
    
    def _calculate_sharpness(self, gray_image: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance."""
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        return float(laplacian.var())
    
    def _calculate_visual_complexity(self, gray_image: np.ndarray) -> float:
        """Calculate visual complexity using edge density."""
        edges = cv2.Canny(gray_image, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size
        return float(edge_density)
    
    def _determine_style_descriptors(self, image: Image.Image, gray_image: np.ndarray) -> List[str]:
        """Determine style descriptors based on image characteristics."""
        descriptors = []
        
        brightness = self._calculate_brightness(gray_image)
        contrast = self._calculate_contrast(gray_image)
        complexity = self._calculate_visual_complexity(gray_image)
        
        # Brightness-based descriptors
        if brightness > 200:
            descriptors.append("bright")
        elif brightness < 50:
            descriptors.append("dark")
        else:
            descriptors.append("balanced")
        
        # Contrast-based descriptors
        if contrast > 70:
            descriptors.append("high-contrast")
        elif contrast < 30:
            descriptors.append("low-contrast")
        
        # Complexity-based descriptors
        if complexity < 0.05:
            descriptors.append("minimalist")
        elif complexity > 0.15:
            descriptors.append("detailed")
        
        # Color-based descriptors
        colors = self._extract_color_palette(image, n_colors=5)
        if len(colors) > 0:
            # Check for monochromatic
            if all(color['hsv']['s'] < 20 for color in colors[:3]):
                descriptors.append("monochromatic")
            # Check for vibrant
            elif any(color['hsv']['s'] > 70 for color in colors[:3]):
                descriptors.append("vibrant")
        
        return descriptors
    
    def _analyze_composition(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze image composition and layout."""
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Convert to grayscale for analysis
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Find regions of interest
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze composition
        composition = {
            "dimensions": {"width": int(width), "height": int(height)},
            "aspect_ratio": round(width / height, 2),
            "rule_of_thirds": self._check_rule_of_thirds(contours, width, height),
            "balance": self._analyze_visual_balance(gray),
            "focal_points": self._find_focal_points(gray),
            "whitespace_ratio": self._calculate_whitespace_ratio(gray)
        }
        
        return composition
    
    def _check_rule_of_thirds(self, contours: List, width: int, height: int) -> Dict[str, Any]:
        """Check if important elements align with rule of thirds."""
        # Define rule of thirds lines
        h_third = height // 3
        w_third = width // 3
        
        intersections = []
        for contour in contours[:10]:  # Check top 10 largest contours
            x, y, w, h = cv2.boundingRect(contour)
            center_x, center_y = x + w // 2, y + h // 2
            
            # Check proximity to rule of thirds lines
            h_distance = min(abs(center_y - h_third), abs(center_y - 2 * h_third))
            w_distance = min(abs(center_x - w_third), abs(center_x - 2 * w_third))
            
            if h_distance < height * 0.05 or w_distance < width * 0.05:
                intersections.append({
                    "x": center_x,
                    "y": center_y,
                    "alignment_score": 1 - (h_distance + w_distance) / (height + width)
                })
        
        return {
            "aligned_elements": len(intersections),
            "alignment_score": float(np.mean([i["alignment_score"] for i in intersections])) if intersections else 0.0
        }
    
    def _analyze_visual_balance(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Analyze visual balance of the image."""
        height, width = gray_image.shape
        
        # Split image into quadrants
        mid_h, mid_w = height // 2, width // 2
        quadrants = {
            "top_left": gray_image[:mid_h, :mid_w],
            "top_right": gray_image[:mid_h, mid_w:],
            "bottom_left": gray_image[mid_h:, :mid_w],
            "bottom_right": gray_image[mid_h:, mid_w:]
        }
        
        # Calculate visual weight for each quadrant
        weights = {}
        for name, quadrant in quadrants.items():
            # Visual weight based on brightness and edge density
            brightness = float(np.mean(quadrant))
            edges = cv2.Canny(quadrant, 50, 150)
            edge_density = float(np.sum(edges > 0)) / edges.size
            weights[name] = brightness * 0.5 + edge_density * 0.5 * 255
        
        # Calculate balance scores
        horizontal_balance = 1 - abs(
            (weights["top_left"] + weights["bottom_left"]) -
            (weights["top_right"] + weights["bottom_right"])
        ) / sum(weights.values())
        
        vertical_balance = 1 - abs(
            (weights["top_left"] + weights["top_right"]) -
            (weights["bottom_left"] + weights["bottom_right"])
        ) / sum(weights.values())
        
        return {
            "horizontal_balance": float(horizontal_balance),
            "vertical_balance": float(vertical_balance),
            "overall_balance": float((horizontal_balance + vertical_balance) / 2)
        }
    
    def _find_focal_points(self, gray_image: np.ndarray) -> List[Dict[str, int]]:
        """Find focal points in the image using corner detection."""
        # Use Harris corner detection
        corners = cv2.cornerHarris(gray_image, 2, 3, 0.04)
        corners = cv2.dilate(corners, None)
        
        # Find top focal points
        threshold = 0.01 * corners.max()
        focal_points = []
        
        # Get coordinates of corners
        y_coords, x_coords = np.where(corners > threshold)
        
        # Cluster nearby points
        if len(x_coords) > 0:
            points = np.column_stack((x_coords, y_coords))
            
            # Simple clustering - group points within 20 pixels
            clustered_points = []
            used = set()
            
            for i, point in enumerate(points):
                if i in used:
                    continue
                
                cluster = [point]
                used.add(i)
                
                for j, other_point in enumerate(points[i+1:], i+1):
                    if j not in used:
                        dist = np.linalg.norm(point - other_point)
                        if dist < 20:
                            cluster.append(other_point)
                            used.add(j)
                
                # Get cluster center
                cluster_center = np.mean(cluster, axis=0).astype(int)
                clustered_points.append({
                    "x": int(cluster_center[0]),
                    "y": int(cluster_center[1]),
                    "strength": float(corners[cluster_center[1], cluster_center[0]])
                })
            
            # Sort by strength and return top 5
            clustered_points.sort(key=lambda p: p["strength"], reverse=True)
            focal_points = clustered_points[:5]
        
        return focal_points
    
    def _calculate_whitespace_ratio(self, gray_image: np.ndarray) -> float:
        """Calculate the ratio of whitespace in the image."""
        # Consider pixels above 240 as whitespace
        whitespace_pixels = float(np.sum(gray_image > 240))
        total_pixels = gray_image.size
        return whitespace_pixels / total_pixels
    
    def _extract_text_elements(self, image_url: str) -> List[Dict[str, Any]]:
        """Extract text elements using AWS Rekognition."""
        if not self.rekognition_available:
            logger.info("Rekognition not available - skipping text extraction")
            return []
            
        try:
            # If S3 URL, use S3 object directly
            if image_url.startswith('s3://'):
                bucket, key = self._parse_s3_url(image_url)
                response = self.rekognition_client.detect_text(
                    Image={'S3Object': {'Bucket': bucket, 'Name': key}}
                )
            else:
                # Download and send as bytes
                response = requests.get(image_url)
                response.raise_for_status()
                response = self.rekognition_client.detect_text(
                    Image={'Bytes': response.content}
                )
            
            text_elements = []
            for text in response.get('TextDetections', []):
                if text['Type'] == 'LINE':
                    text_elements.append({
                        "text": text['DetectedText'],
                        "confidence": float(text['Confidence']),
                        "bounding_box": {
                            "left": float(text['Geometry']['BoundingBox']['Left']),
                            "top": float(text['Geometry']['BoundingBox']['Top']),
                            "width": float(text['Geometry']['BoundingBox']['Width']),
                            "height": float(text['Geometry']['BoundingBox']['Height'])
                        }
                    })
            
            return text_elements
            
        except Exception as e:
            if "AccessDenied" in str(e) or "not authorized" in str(e):
                logger.warning("AWS Rekognition access denied - text extraction disabled")
                self.rekognition_available = False
            else:
                logger.warning(f"Could not extract text: {str(e)}")
            return []
    
    def _analyze_visual_characteristics(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze additional visual characteristics."""
        img_array = np.array(image)
        
        characteristics = {
            "has_transparency": image.mode in ('RGBA', 'LA'),
            "is_monochrome": self._is_monochrome(image),
            "dominant_orientation": self._detect_dominant_orientation(img_array),
            "texture_complexity": self._analyze_texture_complexity(img_array)
        }
        
        return characteristics
    
    def _is_monochrome(self, image: Image.Image) -> bool:
        """Check if image is monochrome."""
        if image.mode == 'L' or image.mode == 'LA':
            return True
        
        # Check if all channels are similar
        img_array = np.array(image.convert('RGB'))
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # If standard deviation between channels is low, it's likely monochrome
        channel_diff = np.std([np.mean(r), np.mean(g), np.mean(b)])
        return channel_diff < 5
    
    def _detect_dominant_orientation(self, img_array: np.ndarray) -> str:
        """Detect dominant orientation (horizontal/vertical/diagonal)."""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Hough line detection
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        
        if lines is not None:
            angles = []
            for line in lines[:20]:  # Consider top 20 lines
                rho, theta = line[0]
                angle = np.degrees(theta)
                angles.append(angle)
            
            # Categorize angles
            horizontal_count = sum(1 for a in angles if 80 <= a <= 100 or -10 <= a <= 10 or 170 <= a <= 190)
            vertical_count = sum(1 for a in angles if 35 <= a <= 55 or 125 <= a <= 145)
            
            if horizontal_count > vertical_count * 1.5:
                return "horizontal"
            elif vertical_count > horizontal_count * 1.5:
                return "vertical"
            else:
                return "mixed"
        
        return "none"
    
    def _analyze_texture_complexity(self, img_array: np.ndarray) -> float:
        """Analyze texture complexity using local binary patterns."""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Texture complexity as normalized gradient variance
        texture_complexity = np.var(gradient_magnitude) / (np.mean(gradient_magnitude) + 1e-6)
        return float(min(texture_complexity / 1000, 1.0))  # Normalize to 0-1
    
    def _detect_brand_elements(self, image_url: str) -> Dict[str, Any]:
        """Detect potential brand elements like logos."""
        if not self.rekognition_available:
            logger.info("Rekognition not available - skipping brand element detection")
            return {
                "has_logo": False,
                "has_text": False,
                "detected_objects": [],
                "brand_indicators": []
            }
            
        try:
            # Use Rekognition to detect labels
            if image_url.startswith('s3://'):
                bucket, key = self._parse_s3_url(image_url)
                response = self.rekognition_client.detect_labels(
                    Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                    MaxLabels=20
                )
            else:
                response = requests.get(image_url)
                response.raise_for_status()
                response = self.rekognition_client.detect_labels(
                    Image={'Bytes': response.content},
                    MaxLabels=20
                )
            
            # Extract relevant brand elements
            brand_elements = {
                "has_logo": False,
                "has_text": False,
                "detected_objects": [],
                "brand_indicators": []
            }
            
            for label in response.get('Labels', []):
                label_name = label['Name'].lower()
                confidence = label['Confidence']
                
                # Check for brand-related labels
                if label_name in ['logo', 'emblem', 'symbol', 'trademark']:
                    brand_elements["has_logo"] = True
                    brand_elements["brand_indicators"].append({
                        "type": "logo",
                        "confidence": confidence
                    })
                elif label_name in ['text', 'document', 'label', 'sign']:
                    brand_elements["has_text"] = True
                
                # Store all detected objects
                brand_elements["detected_objects"].append({
                    "name": label['Name'],
                    "confidence": confidence
                })
            
            return brand_elements
            
        except Exception as e:
            if "AccessDenied" in str(e) or "not authorized" in str(e):
                logger.warning("AWS Rekognition access denied - brand element detection disabled")
                self.rekognition_available = False
            else:
                logger.warning(f"Could not detect brand elements: {str(e)}")
            return {
                "has_logo": False,
                "has_text": False,
                "detected_objects": [],
                "brand_indicators": []
            }
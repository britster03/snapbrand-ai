import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class LayoutPattern(Enum):
    """Common conversion-optimized layout patterns."""
    Z_PATTERN = "z_pattern"  # For content-light designs
    F_PATTERN = "f_pattern"  # For content-heavy designs
    CENTERED = "centered"  # For single focus designs
    GRID = "grid"  # For multiple items
    ASYMMETRIC = "asymmetric"  # For dynamic designs
    GOLDEN_RATIO = "golden_ratio"  # For aesthetic balance


class VisualHierarchy(Enum):
    """Visual hierarchy levels."""
    PRIMARY = 1  # Main focal point (CTA, hero image)
    SECONDARY = 2  # Supporting elements (benefits, features)
    TERTIARY = 3  # Additional info (testimonials, badges)
    BACKGROUND = 4  # Context and atmosphere


class ConversionLayoutEngine:
    """Engine for creating conversion-focused layouts."""
    
    def __init__(self):
        self.golden_ratio = 1.618
        self.rule_of_thirds = 1/3
        self.layout_templates = self._initialize_layout_templates()
        self.psychology_factors = self._initialize_psychology_factors()
    
    def generate_layout_guide(
        self,
        content_type: str,
        conversion_goal: str,
        brand_style: Optional[str] = None,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive layout guide for conversion optimization."""
        
        # Select base layout pattern
        layout_pattern = self._select_layout_pattern(content_type, conversion_goal)
        
        # Get dimensions for platform
        dimensions = self._get_optimal_dimensions(platform or "web")
        
        # Create layout zones
        zones = self._create_layout_zones(layout_pattern, dimensions)
        
        # Apply visual hierarchy
        hierarchy = self._apply_visual_hierarchy(zones, conversion_goal)
        
        # Add psychological triggers
        psychology = self._apply_psychology_factors(conversion_goal, brand_style)
        
        # Generate composition rules
        composition = self._generate_composition_rules(layout_pattern, zones)
        
        return {
            "layout_pattern": layout_pattern.value,
            "dimensions": dimensions,
            "zones": zones,
            "visual_hierarchy": hierarchy,
            "psychology_factors": psychology,
            "composition_rules": composition,
            "implementation_guide": self._create_implementation_guide(
                layout_pattern, zones, hierarchy
            )
        }
    
    def _initialize_layout_templates(self) -> Dict[LayoutPattern, Dict[str, Any]]:
        """Initialize layout pattern templates."""
        return {
            LayoutPattern.Z_PATTERN: {
                "description": "Eye movement follows Z shape - ideal for simple, CTA-focused designs",
                "best_for": ["landing pages", "hero sections", "simple CTAs"],
                "zones": {
                    "top_left": {"purpose": "logo/brand", "weight": 0.15},
                    "top_right": {"purpose": "CTA/navigation", "weight": 0.20},
                    "center": {"purpose": "hero visual", "weight": 0.40},
                    "bottom_left": {"purpose": "supporting info", "weight": 0.10},
                    "bottom_right": {"purpose": "primary CTA", "weight": 0.15}
                }
            },
            LayoutPattern.F_PATTERN: {
                "description": "Eye movement follows F shape - ideal for content-rich designs",
                "best_for": ["blog posts", "product pages", "info-heavy content"],
                "zones": {
                    "header": {"purpose": "key message", "weight": 0.25},
                    "left_sidebar": {"purpose": "navigation/filters", "weight": 0.15},
                    "content_area": {"purpose": "main content", "weight": 0.45},
                    "right_sidebar": {"purpose": "secondary CTAs", "weight": 0.15}
                }
            },
            LayoutPattern.CENTERED: {
                "description": "Central focal point - ideal for single message/product",
                "best_for": ["product showcase", "announcements", "minimalist design"],
                "zones": {
                    "center": {"purpose": "main focal point", "weight": 0.60},
                    "top": {"purpose": "context/headline", "weight": 0.15},
                    "bottom": {"purpose": "CTA", "weight": 0.15},
                    "margins": {"purpose": "breathing room", "weight": 0.10}
                }
            },
            LayoutPattern.GRID: {
                "description": "Organized grid - ideal for multiple items",
                "best_for": ["product catalogs", "portfolios", "comparison layouts"],
                "zones": {
                    "grid_cells": {"purpose": "individual items", "weight": 0.70},
                    "header": {"purpose": "category/filters", "weight": 0.15},
                    "footer": {"purpose": "pagination/CTA", "weight": 0.15}
                }
            },
            LayoutPattern.ASYMMETRIC: {
                "description": "Dynamic asymmetric - ideal for modern, attention-grabbing designs",
                "best_for": ["creative campaigns", "fashion", "innovative products"],
                "zones": {
                    "dominant": {"purpose": "main visual", "weight": 0.50},
                    "supporting": {"purpose": "secondary content", "weight": 0.25},
                    "accent": {"purpose": "CTA/highlight", "weight": 0.15},
                    "negative_space": {"purpose": "visual breathing", "weight": 0.10}
                }
            },
            LayoutPattern.GOLDEN_RATIO: {
                "description": "Golden ratio spiral - ideal for aesthetic, premium designs",
                "best_for": ["luxury products", "artistic content", "premium brands"],
                "zones": {
                    "focal_point": {"purpose": "primary focus", "weight": 0.38},
                    "secondary": {"purpose": "supporting visual", "weight": 0.24},
                    "tertiary": {"purpose": "details/info", "weight": 0.15},
                    "accent": {"purpose": "CTA", "weight": 0.13},
                    "breathing": {"purpose": "whitespace", "weight": 0.10}
                }
            }
        }
    
    def _initialize_psychology_factors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize psychological conversion factors."""
        return {
            "urgency": {
                "colors": ["red", "orange", "warm tones"],
                "elements": ["countdown timers", "limited badges", "flash elements"],
                "positioning": "top and near CTA"
            },
            "trust": {
                "colors": ["blue", "green", "neutral tones"],
                "elements": ["badges", "testimonials", "certifications"],
                "positioning": "near decision points"
            },
            "value": {
                "colors": ["gold", "green", "contrasting"],
                "elements": ["price comparisons", "savings badges", "value props"],
                "positioning": "prominent, above fold"
            },
            "social_proof": {
                "colors": ["brand consistent"],
                "elements": ["reviews", "user photos", "statistics"],
                "positioning": "supporting main message"
            },
            "scarcity": {
                "colors": ["red", "urgent tones"],
                "elements": ["stock counters", "exclusive badges", "limited text"],
                "positioning": "near product/CTA"
            }
        }
    
    def _select_layout_pattern(
        self,
        content_type: str,
        conversion_goal: str
    ) -> LayoutPattern:
        """Select optimal layout pattern based on content and goals."""
        
        # Decision matrix for layout selection
        selection_matrix = {
            ("hero_banner", "sales"): LayoutPattern.Z_PATTERN,
            ("hero_banner", "awareness"): LayoutPattern.CENTERED,
            ("product_showcase", "sales"): LayoutPattern.CENTERED,
            ("product_grid", "browse"): LayoutPattern.GRID,
            ("landing_page", "conversion"): LayoutPattern.Z_PATTERN,
            ("content_rich", "engagement"): LayoutPattern.F_PATTERN,
            ("premium_product", "desire"): LayoutPattern.GOLDEN_RATIO,
            ("creative_campaign", "attention"): LayoutPattern.ASYMMETRIC
        }
        
        # Try to find exact match
        key = (content_type, conversion_goal)
        if key in selection_matrix:
            return selection_matrix[key]
        
        # Fallback logic
        if "grid" in content_type or "multiple" in content_type:
            return LayoutPattern.GRID
        elif "premium" in conversion_goal or "luxury" in content_type:
            return LayoutPattern.GOLDEN_RATIO
        elif "simple" in content_type or "cta" in conversion_goal:
            return LayoutPattern.Z_PATTERN
        else:
            return LayoutPattern.CENTERED
    
    def _get_optimal_dimensions(self, platform: str) -> Dict[str, int]:
        """Get optimal dimensions for platform."""
        
        dimensions = {
            "web": {"width": 1920, "height": 800},
            "mobile": {"width": 1080, "height": 1920},
            "instagram_square": {"width": 1080, "height": 1080},
            "instagram_story": {"width": 1080, "height": 1920},
            "facebook": {"width": 1200, "height": 630},
            "twitter": {"width": 1200, "height": 675},
            "linkedin": {"width": 1200, "height": 627},
            "email": {"width": 600, "height": 300},
            "banner": {"width": 1920, "height": 600}
        }
        
        return dimensions.get(platform, dimensions["web"])
    
    def _create_layout_zones(
        self,
        pattern: LayoutPattern,
        dimensions: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Create specific layout zones based on pattern and dimensions."""
        
        width = dimensions["width"]
        height = dimensions["height"]
        zones = []
        
        if pattern == LayoutPattern.Z_PATTERN:
            zones = [
                {
                    "name": "logo_zone",
                    "bounds": {"x": 0, "y": 0, "w": width * 0.25, "h": height * 0.15},
                    "purpose": "brand identity",
                    "hierarchy": VisualHierarchy.SECONDARY
                },
                {
                    "name": "top_cta_zone",
                    "bounds": {"x": width * 0.75, "y": 0, "w": width * 0.25, "h": height * 0.15},
                    "purpose": "secondary CTA",
                    "hierarchy": VisualHierarchy.SECONDARY
                },
                {
                    "name": "hero_zone",
                    "bounds": {"x": width * 0.1, "y": height * 0.2, "w": width * 0.8, "h": height * 0.5},
                    "purpose": "main visual/message",
                    "hierarchy": VisualHierarchy.PRIMARY
                },
                {
                    "name": "bottom_cta_zone",
                    "bounds": {"x": width * 0.6, "y": height * 0.75, "w": width * 0.3, "h": height * 0.15},
                    "purpose": "primary CTA",
                    "hierarchy": VisualHierarchy.PRIMARY
                }
            ]
            
        elif pattern == LayoutPattern.CENTERED:
            center_size = min(width, height) * 0.6
            zones = [
                {
                    "name": "main_zone",
                    "bounds": {
                        "x": (width - center_size) / 2,
                        "y": (height - center_size) / 2,
                        "w": center_size,
                        "h": center_size
                    },
                    "purpose": "focal point",
                    "hierarchy": VisualHierarchy.PRIMARY
                },
                {
                    "name": "title_zone",
                    "bounds": {
                        "x": width * 0.1,
                        "y": height * 0.05,
                        "w": width * 0.8,
                        "h": height * 0.15
                    },
                    "purpose": "headline",
                    "hierarchy": VisualHierarchy.SECONDARY
                },
                {
                    "name": "cta_zone",
                    "bounds": {
                        "x": width * 0.3,
                        "y": height * 0.8,
                        "w": width * 0.4,
                        "h": height * 0.1
                    },
                    "purpose": "call to action",
                    "hierarchy": VisualHierarchy.PRIMARY
                }
            ]
            
        elif pattern == LayoutPattern.GOLDEN_RATIO:
            # Calculate golden ratio spiral zones
            phi = self.golden_ratio
            zones = self._calculate_golden_ratio_zones(width, height, phi)
            
        elif pattern == LayoutPattern.GRID:
            # Create grid zones
            zones = self._create_grid_zones(width, height, columns=3, rows=2)
            
        elif pattern == LayoutPattern.F_PATTERN:
            zones = self._create_f_pattern_zones(width, height)
            
        elif pattern == LayoutPattern.ASYMMETRIC:
            zones = self._create_asymmetric_zones(width, height)
        
        return zones
    
    def _calculate_golden_ratio_zones(
        self,
        width: int,
        height: int,
        phi: float
    ) -> List[Dict[str, Any]]:
        """Calculate zones based on golden ratio."""
        
        # Main focal area using golden ratio
        focal_width = width / phi
        focal_height = height / phi
        
        zones = [
            {
                "name": "primary_focal",
                "bounds": {
                    "x": width - focal_width,
                    "y": 0,
                    "w": focal_width,
                    "h": focal_height
                },
                "purpose": "main focal point",
                "hierarchy": VisualHierarchy.PRIMARY
            },
            {
                "name": "secondary_area",
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "w": width - focal_width,
                    "h": focal_height
                },
                "purpose": "supporting content",
                "hierarchy": VisualHierarchy.SECONDARY
            },
            {
                "name": "tertiary_area",
                "bounds": {
                    "x": 0,
                    "y": focal_height,
                    "w": width,
                    "h": height - focal_height
                },
                "purpose": "additional info",
                "hierarchy": VisualHierarchy.TERTIARY
            }
        ]
        
        return zones
    
    def _create_grid_zones(
        self,
        width: int,
        height: int,
        columns: int,
        rows: int
    ) -> List[Dict[str, Any]]:
        """Create grid-based zones."""
        
        zones = []
        cell_width = width / columns
        cell_height = height / rows
        padding = min(cell_width, cell_height) * 0.05
        
        for row in range(rows):
            for col in range(columns):
                zones.append({
                    "name": f"grid_cell_{row}_{col}",
                    "bounds": {
                        "x": col * cell_width + padding,
                        "y": row * cell_height + padding,
                        "w": cell_width - 2 * padding,
                        "h": cell_height - 2 * padding
                    },
                    "purpose": "content cell",
                    "hierarchy": VisualHierarchy.SECONDARY
                })
        
        return zones
    
    def _create_f_pattern_zones(self, width: int, height: int) -> List[Dict[str, Any]]:
        """Create F-pattern layout zones."""
        
        header_height = height * 0.15
        sidebar_width = width * 0.25
        
        zones = [
            {
                "name": "header",
                "bounds": {"x": 0, "y": 0, "w": width, "h": header_height},
                "purpose": "primary message/navigation",
                "hierarchy": VisualHierarchy.PRIMARY
            },
            {
                "name": "left_sidebar",
                "bounds": {"x": 0, "y": header_height, "w": sidebar_width, "h": height - header_height},
                "purpose": "navigation/filters",
                "hierarchy": VisualHierarchy.SECONDARY
            },
            {
                "name": "content_area",
                "bounds": {
                    "x": sidebar_width,
                    "y": header_height,
                    "w": width - sidebar_width,
                    "h": height - header_height
                },
                "purpose": "main content",
                "hierarchy": VisualHierarchy.PRIMARY
            }
        ]
        
        return zones
    
    def _create_asymmetric_zones(self, width: int, height: int) -> List[Dict[str, Any]]:
        """Create asymmetric layout zones for dynamic designs."""
        
        # Create interesting asymmetric divisions
        zones = [
            {
                "name": "dominant_visual",
                "bounds": {
                    "x": width * 0.4,
                    "y": 0,
                    "w": width * 0.6,
                    "h": height * 0.7
                },
                "purpose": "main visual impact",
                "hierarchy": VisualHierarchy.PRIMARY
            },
            {
                "name": "content_block",
                "bounds": {
                    "x": 0,
                    "y": height * 0.2,
                    "w": width * 0.35,
                    "h": height * 0.5
                },
                "purpose": "message/content",
                "hierarchy": VisualHierarchy.SECONDARY
            },
            {
                "name": "cta_accent",
                "bounds": {
                    "x": width * 0.1,
                    "y": height * 0.75,
                    "w": width * 0.3,
                    "h": height * 0.15
                },
                "purpose": "call to action",
                "hierarchy": VisualHierarchy.PRIMARY
            }
        ]
        
        return zones
    
    def _apply_visual_hierarchy(
        self,
        zones: List[Dict[str, Any]],
        conversion_goal: str
    ) -> Dict[str, Any]:
        """Apply visual hierarchy principles to zones."""
        
        hierarchy_rules = {
            "size": "Primary elements 2-3x larger than secondary",
            "contrast": "High contrast for CTAs and key messages",
            "position": "Important elements in natural eye path",
            "whitespace": "More space around important elements",
            "color": "Bright/contrasting colors for primary elements"
        }
        
        # Adjust hierarchy based on conversion goal
        if conversion_goal == "sales":
            primary_focus = "product and price"
            secondary_focus = "benefits and trust signals"
        elif conversion_goal == "leads":
            primary_focus = "value proposition and form"
            secondary_focus = "social proof and benefits"
        elif conversion_goal == "awareness":
            primary_focus = "brand message and visual"
            secondary_focus = "call to action"
        else:
            primary_focus = "main message"
            secondary_focus = "supporting elements"
        
        return {
            "rules": hierarchy_rules,
            "primary_focus": primary_focus,
            "secondary_focus": secondary_focus,
            "visual_weight_distribution": self._calculate_visual_weights(zones)
        }
    
    def _calculate_visual_weights(self, zones: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate visual weight distribution across zones."""
        
        total_area = sum(
            zone["bounds"]["w"] * zone["bounds"]["h"]
            for zone in zones
        )
        
        weights = {}
        for zone in zones:
            area = zone["bounds"]["w"] * zone["bounds"]["h"]
            hierarchy_multiplier = {
                VisualHierarchy.PRIMARY: 2.0,
                VisualHierarchy.SECONDARY: 1.0,
                VisualHierarchy.TERTIARY: 0.5,
                VisualHierarchy.BACKGROUND: 0.25
            }.get(zone.get("hierarchy", VisualHierarchy.SECONDARY), 1.0)
            
            weights[zone["name"]] = (area / total_area) * hierarchy_multiplier
        
        # Normalize weights
        total_weight = sum(weights.values())
        for zone_name in weights:
            weights[zone_name] = weights[zone_name] / total_weight
        
        return weights
    
    def _apply_psychology_factors(
        self,
        conversion_goal: str,
        brand_style: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Apply psychological conversion factors."""
        
        factors = []
        
        # Goal-based psychology
        goal_psychology = {
            "sales": ["urgency", "value", "scarcity"],
            "leads": ["trust", "value", "social_proof"],
            "awareness": ["curiosity", "emotion", "memorability"],
            "engagement": ["relatability", "social_proof", "emotion"]
        }
        
        selected_factors = goal_psychology.get(conversion_goal, ["trust", "value"])
        
        for factor in selected_factors:
            if factor in self.psychology_factors:
                factors.append({
                    "factor": factor,
                    "implementation": self.psychology_factors[factor],
                    "priority": "high" if factor in selected_factors[:2] else "medium"
                })
        
        return factors
    
    def _generate_composition_rules(
        self,
        pattern: LayoutPattern,
        zones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate specific composition rules for the layout."""
        
        rules = {
            "alignment": self._get_alignment_rules(pattern),
            "spacing": self._get_spacing_rules(pattern),
            "visual_flow": self._get_visual_flow_rules(pattern),
            "balance": self._get_balance_rules(zones),
            "focal_points": self._get_focal_point_rules(zones)
        }
        
        return rules
    
    def _get_alignment_rules(self, pattern: LayoutPattern) -> List[str]:
        """Get alignment rules for the pattern."""
        
        alignment_rules = {
            LayoutPattern.Z_PATTERN: [
                "Align key elements along Z-path",
                "Keep CTAs on the right for natural flow",
                "Maintain consistent margins"
            ],
            LayoutPattern.F_PATTERN: [
                "Strong left alignment for content",
                "Horizontal alignment for scan lines",
                "Consistent gutters between sections"
            ],
            LayoutPattern.CENTERED: [
                "Perfect center alignment for main element",
                "Supporting elements balanced around center",
                "Symmetrical spacing"
            ],
            LayoutPattern.GRID: [
                "Consistent grid alignment",
                "Equal spacing between cells",
                "Aligned baselines for text"
            ],
            LayoutPattern.ASYMMETRIC: [
                "Intentional misalignment for interest",
                "Hidden grid for structure",
                "Strategic breaking of alignment"
            ],
            LayoutPattern.GOLDEN_RATIO: [
                "Align to golden ratio proportions",
                "Natural spiral flow",
                "Harmonious proportions"
            ]
        }
        
        return alignment_rules.get(pattern, ["Maintain visual consistency"])
    
    def _get_spacing_rules(self, pattern: LayoutPattern) -> Dict[str, Any]:
        """Get spacing rules for the pattern."""
        
        return {
            "minimum_padding": "5% of container dimension",
            "element_spacing": "Related: 1x, Unrelated: 2-3x base unit",
            "whitespace_ratio": "30-40% for optimal readability",
            "breathing_room": "Increase space around CTAs by 50%"
        }
    
    def _get_visual_flow_rules(self, pattern: LayoutPattern) -> List[str]:
        """Get visual flow rules for the pattern."""
        
        flow_rules = {
            LayoutPattern.Z_PATTERN: [
                "Top-left → Top-right → Center → Bottom-right",
                "Natural reading pattern for Western audiences",
                "Clear path to CTA"
            ],
            LayoutPattern.F_PATTERN: [
                "Horizontal scanning pattern",
                "Important info in scan lines",
                "Decreasing importance down the page"
            ],
            LayoutPattern.CENTERED: [
                "Immediate focus on center",
                "Radial flow outward",
                "Return to center for CTA"
            ]
        }
        
        return flow_rules.get(pattern, ["Guide eye to conversion point"])
    
    def _get_balance_rules(self, zones: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get balance rules based on zones."""
        
        # Calculate center of visual weight
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        for zone in zones:
            bounds = zone["bounds"]
            center_x = bounds["x"] + bounds["w"] / 2
            center_y = bounds["y"] + bounds["h"] / 2
            area = bounds["w"] * bounds["h"]
            
            weighted_x += center_x * area
            weighted_y += center_y * area
            total_weight += area
        
        if total_weight > 0:
            visual_center_x = weighted_x / total_weight
            visual_center_y = weighted_y / total_weight
        else:
            visual_center_x = visual_center_y = 0.5
        
        return {
            "visual_center": f"({visual_center_x:.1f}, {visual_center_y:.1f})",
            "balance_type": "symmetric" if abs(visual_center_x - 0.5) < 0.1 else "asymmetric",
            "recommendation": "Adjust element weights to achieve desired balance"
        }
    
    def _get_focal_point_rules(self, zones: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get focal point rules."""
        
        focal_points = []
        
        for zone in zones:
            if zone.get("hierarchy") == VisualHierarchy.PRIMARY:
                focal_points.append({
                    "zone": zone["name"],
                    "techniques": [
                        "High contrast",
                        "Larger size",
                        "Isolation/whitespace",
                        "Bright colors",
                        "Sharp focus"
                    ]
                })
        
        return focal_points
    
    def _create_implementation_guide(
        self,
        pattern: LayoutPattern,
        zones: List[Dict[str, Any]],
        hierarchy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create practical implementation guide."""
        
        return {
            "prompt_guidance": self._generate_prompt_guidance(pattern, zones),
            "color_strategy": self._generate_color_strategy(hierarchy),
            "text_placement": self._generate_text_placement_guide(zones),
            "cta_optimization": self._generate_cta_guide(zones),
            "testing_recommendations": self._generate_testing_recommendations()
        }
    
    def _generate_prompt_guidance(
        self,
        pattern: LayoutPattern,
        zones: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate prompts for AI image generation."""
        
        pattern_prompts = {
            LayoutPattern.Z_PATTERN: "Z-pattern layout, clear visual hierarchy, eye-flow from top-left to bottom-right",
            LayoutPattern.F_PATTERN: "F-pattern layout, content-rich design, horizontal scanning lines",
            LayoutPattern.CENTERED: "centered composition, strong focal point, balanced symmetry",
            LayoutPattern.GRID: "grid layout, organized structure, consistent spacing",
            LayoutPattern.ASYMMETRIC: "dynamic asymmetric layout, modern composition, visual tension",
            LayoutPattern.GOLDEN_RATIO: "golden ratio composition, aesthetic balance, harmonious proportions"
        }
        
        prompts = [pattern_prompts.get(pattern, "balanced composition")]
        
        # Add zone-specific prompts
        for zone in zones:
            if zone.get("hierarchy") == VisualHierarchy.PRIMARY:
                prompts.append(f"{zone['purpose']} as main focal point")
        
        return prompts
    
    def _generate_color_strategy(self, hierarchy: Dict[str, Any]) -> Dict[str, str]:
        """Generate color strategy for conversion."""
        
        return {
            "primary_action": "High contrast color (complementary to brand)",
            "secondary_elements": "Brand colors at 70% saturation",
            "background": "Neutral or very desaturated brand color",
            "accents": "Sparingly used bright colors for urgency",
            "text": "High readability contrast ratios (WCAG AA minimum)"
        }
    
    def _generate_text_placement_guide(self, zones: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate text placement guidelines."""
        
        guidelines = []
        
        for zone in zones:
            if zone["purpose"] in ["headline", "main message", "CTA"]:
                guidelines.append({
                    "zone": zone["name"],
                    "text_size": "Large" if zone.get("hierarchy") == VisualHierarchy.PRIMARY else "Medium",
                    "alignment": "Center" if "cta" in zone["purpose"].lower() else "Left",
                    "contrast": "Maximum" if "cta" in zone["purpose"].lower() else "High"
                })
        
        return guidelines
    
    def _generate_cta_guide(self, zones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate CTA optimization guide."""
        
        cta_zones = [z for z in zones if "cta" in z.get("purpose", "").lower()]
        
        return {
            "placement": "Multiple CTAs in natural flow points" if len(cta_zones) > 1 else "Single prominent CTA",
            "size": "Minimum 44x44px touch target, prefer larger",
            "color": "Contrasting color, different from other elements",
            "spacing": "150% normal spacing around CTA",
            "copy": "Action-oriented, specific, urgent",
            "design": "Subtle shadow/3D effect for clickability"
        }
    
    def _generate_testing_recommendations(self) -> List[str]:
        """Generate A/B testing recommendations."""
        
        return [
            "Test CTA placement: current vs 10% higher",
            "Test color contrast: current vs higher contrast version",
            "Test urgency elements: with vs without",
            "Test social proof placement: near CTA vs separate section",
            "Test headline size: current vs 20% larger",
            "Test whitespace: current vs 20% more breathing room"
        ]
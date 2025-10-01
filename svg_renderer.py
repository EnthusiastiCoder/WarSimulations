import os
import xml.etree.ElementTree as ET
from troop_animator import TroopAnimator
from health_bar_animator import HealthBarAnimator
from arrow_animator import ArrowAnimator

class SVGRenderer:
    """Handles SVG animation generation for battlefield"""
    
    def __init__(self, battlefield):
        self.battlefield = battlefield
        self.troop_animator = TroopAnimator(battlefield)
        self.health_bar_animator = HealthBarAnimator(battlefield)
        self.arrow_animator = ArrowAnimator(battlefield)
    
    def create_animated_svg(self, scale=20, frame_duration=0.5):
        """Create an animated SVG from the battlefield data"""
        if not self.battlefield.animation_frames:
            print("No animation frames captured.")
            return None
            
        # Check if output folder exists
        if not hasattr(self.battlefield.png_renderer, 'output_folder') or not self.battlefield.png_renderer.output_folder:
            print("No output folder found.")
            return None
        
        # Calculate SVG dimensions
        width = self.battlefield.width * scale
        height = self.battlefield.height * scale
        
        # Create SVG root element
        svg = ET.Element('svg', {
            'width': str(width),
            'height': str(height),
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f'0 0 {width} {height}'
        })
        
        # Add background
        ET.SubElement(svg, 'rect', {
            'width': str(width),
            'height': str(height),
            'fill': '#8B4513'  # Brown background
        })
        
        # Get all unique troop IDs that ever existed
        all_troop_ids = self._get_all_troop_ids()
        
        # Add troop elements and animations
        for troop_id in all_troop_ids:
            self._add_troop_elements(svg, troop_id, scale, frame_duration)
        
        # Add arrow animations
        self.arrow_animator.add_arrow_animations(svg, scale, frame_duration)
        
        # Save to file
        svg_path = os.path.join(self.battlefield.png_renderer.output_folder, "battle_animation.svg")
        svg_content = self._svg_to_string(svg)
        
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"Animated SVG saved to {svg_path}")
        return svg_path
    
    def _get_all_troop_ids(self):
        """Get all unique troop IDs that ever existed in any frame"""
        all_troop_ids = set()
        for frame in self.battlefield.animation_frames:
            for troop in frame['troops']:
                all_troop_ids.add(troop['id'])
        return all_troop_ids
    
    def _add_troop_elements(self, svg, troop_id, scale, frame_duration):
        """Add troop shape, health bar, and animations for a specific troop"""
        # Get troop info from first frame where it appears
        troop_info = self._get_troop_info(troop_id)
        if not troop_info:
            return
        
        size = int(scale * 0.7)
        
        # Create troop shape based on type
        if troop_info['type'] == 'barbarian':
            # Create circle for barbarian
            shape = ET.SubElement(svg, 'circle', {
                'r': str(size // 2),
                'fill': troop_info['color'],
                'stroke': 'black',
                'stroke-width': '2',
                'opacity': '1'
            })
            shape_type = 'circle'
        else:  # archer
            # Create square for archer (offset to center it properly)
            rect_size = size  # Make it a proper square
            shape = ET.SubElement(svg, 'rect', {
                'width': str(rect_size),
                'height': str(rect_size),
                'x': str(-rect_size // 2),  # Center horizontally
                'y': str(-rect_size // 2),  # Center vertically
                'fill': troop_info['color'],
                'stroke': 'black',
                'stroke-width': '2',
                'opacity': '1'
            })
            shape_type = 'rect'
        
        # Add animations to troop
        self.troop_animator.add_position_animation(shape, troop_id, shape_type, scale, frame_duration)
        self.troop_animator.add_visibility_animation(shape, troop_id, frame_duration)
        
        # Add health bar
        self.health_bar_animator.add_health_bar(svg, troop_id, shape_type, scale, frame_duration)
    
    def _get_troop_info(self, troop_id):
        """Get basic troop information from first appearance"""
        for frame in self.battlefield.animation_frames:
            for troop in frame['troops']:
                if troop['id'] == troop_id:
                    return {
                        'color': '#0080FF' if troop['team'] == 0 else '#FF4040',
                        'type': troop['type']
                    }
        return None
    
    def _svg_to_string(self, svg):
        """Convert SVG element to formatted string"""
        # Convert to string with proper formatting
        rough_string = ET.tostring(svg, encoding='unicode')
        
        # Add XML declaration
        formatted_svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + rough_string
        
        return formatted_svg
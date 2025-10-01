import xml.etree.ElementTree as ET

class TroopAnimator:
    """Handles troop position and visibility animations for SVG generation"""
    
    def __init__(self, battlefield):
        self.battlefield = battlefield
    
    def add_position_animation(self, element, troop_id, troop_type, scale, frame_duration):
        """Add position animation to a troop element"""
        x_values = []
        y_values = []
        
        size = int(scale * 0.7)  # Same size calculation as in svg_renderer
        
        for frame in self.battlefield.animation_frames:
            troop_data = self._find_troop_in_frame(frame, troop_id)
            if troop_data:
                x = troop_data['position'][0] * scale
                y = troop_data['position'][1] * scale
                
                if troop_type == 'rect':
                    # For rectangles, offset to center them (x,y is top-left corner)
                    x -= size // 2
                    y -= size // 2
                
                x_values.append(str(int(x)))
                y_values.append(str(int(y)))
            else:
                # Troop is dead - keep last known position
                if x_values:
                    x_values.append(x_values[-1])
                    y_values.append(y_values[-1])
                else:
                    x_values.append('0')
                    y_values.append('0')
        
        if len(x_values) > 1:
            total_duration = len(self.battlefield.animation_frames) * frame_duration
            
            # Add position animations
            if troop_type == 'circle':
                # For circles, animate cx and cy
                ET.SubElement(element, 'animate', {
                    'attributeName': 'cx',
                    'values': ';'.join(x_values),
                    'dur': f'{total_duration}s',
                    'repeatCount': 'indefinite'
                })
                ET.SubElement(element, 'animate', {
                    'attributeName': 'cy',
                    'values': ';'.join(y_values),
                    'dur': f'{total_duration}s',
                    'repeatCount': 'indefinite'
                })
            elif troop_type == 'rect':
                # For rectangles, animate x and y
                ET.SubElement(element, 'animate', {
                    'attributeName': 'x',
                    'values': ';'.join(x_values),
                    'dur': f'{total_duration}s',
                    'repeatCount': 'indefinite'
                })
                ET.SubElement(element, 'animate', {
                    'attributeName': 'y',
                    'values': ';'.join(y_values),
                    'dur': f'{total_duration}s',
                    'repeatCount': 'indefinite'
                })
    
    def add_visibility_animation(self, element, troop_id, frame_duration):
        """Add visibility animation to show/hide troops when they die"""
        opacity_values = []
        
        for frame in self.battlefield.animation_frames:
            troop_data = self._find_troop_in_frame(frame, troop_id)
            if troop_data and troop_data['alive']:
                opacity_values.append('1')
            else:
                opacity_values.append('0')
        
        if len(opacity_values) > 1:
            total_duration = len(self.battlefield.animation_frames) * frame_duration
            
            ET.SubElement(element, 'animate', {
                'attributeName': 'opacity',
                'values': ';'.join(opacity_values),
                'dur': f'{total_duration}s',
                'repeatCount': 'indefinite'
            })
    
    def _find_troop_in_frame(self, frame, troop_id):
        """Find troop data in a frame by ID"""
        for troop in frame['troops']:
            if troop['id'] == troop_id:
                return troop
        return None
import xml.etree.ElementTree as ET

class HealthBarAnimator:
    """Handles health bar animations for SVG generation"""
    
    def __init__(self, battlefield):
        self.battlefield = battlefield
    
    def add_health_bar(self, svg, troop_id, troop_type, scale, frame_duration):
        """Add health bar elements and animations for a troop"""
        size = int(scale * 0.7)
        bar_width = int(scale * 0.8)
        bar_height = int(scale * 0.15)
        
        # Create background rectangle (red for missing health)
        bg_rect = ET.SubElement(svg, 'rect', {
            'width': str(bar_width),
            'height': str(bar_height),
            'fill': 'red',
            'stroke': 'black',
            'stroke-width': '1',
            'opacity': '1'
        })
        
        # Create health rectangle (green for current health)
        health_rect = ET.SubElement(svg, 'rect', {
            'height': str(bar_height),
            'fill': 'green',
            'opacity': '1'
        })
        
        # Add animations
        self._add_health_bar_animation(bg_rect, health_rect, troop_id, troop_type, scale, 
                                     frame_duration, bar_width, bar_height, size)
        
        return bg_rect, health_rect
    
    def _add_health_bar_animation(self, bg_rect, health_rect, troop_id, troop_type, scale, 
                                frame_duration, bar_width, bar_height, size):
        """Add position and health animations to health bar elements"""
        # Collect animation data
        bg_x_values = []
        bg_y_values = []
        health_x_values = []
        health_y_values = []
        health_width_values = []
        opacity_values = []
        
        for frame in self.battlefield.animation_frames:
            troop_data = self._find_troop_in_frame(frame, troop_id)
            
            if troop_data and troop_data['alive']:
                # Troop is alive - show health bar
                x = troop_data['position'][0] * scale
                y = troop_data['position'][1] * scale
                
                # Position health bar above troop
                bar_x = x - bar_width // 2
                bar_y = y - size // 2 - bar_height - 3
                
                bg_x_values.append(str(int(bar_x)))
                bg_y_values.append(str(int(bar_y)))
                health_x_values.append(str(int(bar_x)))
                health_y_values.append(str(int(bar_y)))
                
                # Calculate health width
                health_ratio = troop_data['health_ratio']
                health_width = int(bar_width * health_ratio)
                health_width_values.append(str(health_width))
                opacity_values.append('1')
            else:
                # Troop is dead - hide health bar
                if bg_x_values:
                    # Keep last position but hide
                    bg_x_values.append(bg_x_values[-1])
                    bg_y_values.append(bg_y_values[-1])
                    health_x_values.append(health_x_values[-1])
                    health_y_values.append(health_y_values[-1])
                    health_width_values.append(health_width_values[-1])
                else:
                    # No previous position
                    bg_x_values.append('0')
                    bg_y_values.append('0')
                    health_x_values.append('0')
                    health_y_values.append('0')
                    health_width_values.append('0')
                opacity_values.append('0')
        
        # Add animations if we have data
        if len(bg_x_values) > 1:
            total_duration = len(self.battlefield.animation_frames) * frame_duration
            
            # Background rectangle animations
            ET.SubElement(bg_rect, 'animate', {
                'attributeName': 'x',
                'values': ';'.join(bg_x_values),
                'dur': f'{total_duration}s',
                'repeatCount': 'indefinite'
            })
            ET.SubElement(bg_rect, 'animate', {
                'attributeName': 'y',
                'values': ';'.join(bg_y_values),
                'dur': f'{total_duration}s',
                'repeatCount': 'indefinite'
            })
            ET.SubElement(bg_rect, 'animate', {
                'attributeName': 'opacity',
                'values': ';'.join(opacity_values),
                'dur': f'{total_duration}s',
                'repeatCount': 'indefinite'
            })
            
            # Health rectangle animations
            ET.SubElement(health_rect, 'animate', {
                'attributeName': 'x',
                'values': ';'.join(health_x_values),
                'dur': f'{total_duration}s',
                'repeatCount': 'indefinite'
            })
            ET.SubElement(health_rect, 'animate', {
                'attributeName': 'y',
                'values': ';'.join(health_y_values),
                'dur': f'{total_duration}s',
                'repeatCount': 'indefinite'
            })
            ET.SubElement(health_rect, 'animate', {
                'attributeName': 'width',
                'values': ';'.join(health_width_values),
                'dur': f'{total_duration}s',
                'repeatCount': 'indefinite'
            })
            ET.SubElement(health_rect, 'animate', {
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
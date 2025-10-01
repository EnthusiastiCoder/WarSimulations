import xml.etree.ElementTree as ET

class ArrowAnimator:
    """Handles arrow animations for SVG generation"""
    
    def __init__(self, battlefield):
        self.battlefield = battlefield
    
    def add_arrow_animations(self, svg, scale, frame_duration):
        """Add all arrow animations to the SVG"""
        if not self.battlefield.animation_frames:
            return
        
        # Collect all unique troop IDs that ever existed in any frame
        all_troop_ids = set()
        for frame in self.battlefield.animation_frames:
            for troop in frame['troops']:
                all_troop_ids.add(troop['id'])
        
        print(f"Creating arrows for {len(all_troop_ids)} unique troops that existed during simulation")
        
        # Create arrows - one per troop that ever existed
        for troop_id in all_troop_ids:
            self._create_troop_arrow(svg, troop_id, scale, frame_duration)
    
    def _create_troop_arrow(self, svg, troop_id, scale, frame_duration):
        """Create one arrow for a troop that follows its targets"""
        # Create line and arrowhead elements with initial hidden state
        line = ET.SubElement(svg, 'line', {
            'stroke': 'red',
            'stroke-width': '3',
            'opacity': '0',
            'x1': '0',
            'y1': '0', 
            'x2': '0',
            'y2': '0'
        })
        
        arrowhead = ET.SubElement(svg, 'polygon', {
            'fill': 'red',
            'opacity': '0',
            'points': '0,0 0,0 0,0'
        })
        
        # Collect animation data for this troop's arrow
        animation_data = self._collect_arrow_animation_data(troop_id, scale)
        
        # Add animations if we have data
        if len(animation_data['x1_values']) > 1:
            self._add_arrow_animations_to_elements(line, arrowhead, animation_data, frame_duration)
    
    def _collect_arrow_animation_data(self, troop_id, scale):
        """Collect all animation data for a specific troop's arrow"""
        x1_values = []  # Arrow base (follows this troop)
        y1_values = []
        x2_values = []  # Arrow head (follows current target)
        y2_values = []
        colors = []
        stroke_styles = []
        opacity_values = []
        arrowhead_points = []
        
        size = int(scale * 0.7)
        last_arrow_pos = None
        
        for frame in self.battlefield.animation_frames:
            # Find this troop in the current frame
            troop_data = self._find_troop_in_frame(frame, troop_id)
            
            if not troop_data:
                # Troop doesn't exist (died) - use last known position or stay hidden
                if last_arrow_pos:
                    self._append_last_known_position(x1_values, y1_values, x2_values, y2_values,
                                                   colors, stroke_styles, opacity_values, 
                                                   arrowhead_points, last_arrow_pos)
                else:
                    self._append_hidden_position(x1_values, y1_values, x2_values, y2_values,
                                               colors, stroke_styles, opacity_values, arrowhead_points)
                continue
            
            # Find if this troop has an arrow in this frame
            troop_arrow = self._find_arrow_in_frame(frame, troop_id)
            
            if troop_arrow:
                # Troop has a target - show arrow
                arrow_pos = self._calculate_arrow_position(troop_arrow, scale, size)
                last_arrow_pos = arrow_pos  # Save for later fade-out
                
                self._append_arrow_position(x1_values, y1_values, x2_values, y2_values,
                                          colors, stroke_styles, opacity_values, 
                                          arrowhead_points, arrow_pos)
            else:
                # Troop has no target - fade arrow at last known position
                if last_arrow_pos:
                    self._append_fade_out_position(x1_values, y1_values, x2_values, y2_values,
                                                 colors, stroke_styles, opacity_values, 
                                                 arrowhead_points, last_arrow_pos)
                else:
                    self._append_hidden_position(x1_values, y1_values, x2_values, y2_values,
                                               colors, stroke_styles, opacity_values, arrowhead_points)
        
        return {
            'x1_values': x1_values,
            'y1_values': y1_values,
            'x2_values': x2_values,
            'y2_values': y2_values,
            'colors': colors,
            'stroke_styles': stroke_styles,
            'opacity_values': opacity_values,
            'arrowhead_points': arrowhead_points
        }
    
    def _find_troop_in_frame(self, frame, troop_id):
        """Find troop data in a frame by ID"""
        for troop in frame['troops']:
            if troop['id'] == troop_id:
                return troop
        return None
    
    def _find_arrow_in_frame(self, frame, troop_id):
        """Find arrow data in a frame by troop ID"""
        for arrow in frame['arrows']:
            if arrow['from_id'] == troop_id:
                return arrow
        return None
    
    def _calculate_arrow_position(self, troop_arrow, scale, size):
        """Calculate arrow position and appearance from arrow data"""
        from_x = troop_arrow['from_pos'][0] * scale
        from_y = troop_arrow['from_pos'][1] * scale
        to_x = troop_arrow['to_pos'][0] * scale
        to_y = troop_arrow['to_pos'][1] * scale
        
        # Calculate direction and positions
        dx = to_x - from_x
        dy = to_y - from_y
        length = (dx*dx + dy*dy)**0.5
        
        if length > 0:
            unit_dx = dx / length
            unit_dy = dy / length
            
            # Arrow base follows this troop (with smaller offset to get closer)
            start_x = from_x + unit_dx * (size * 0.7)
            start_y = from_y + unit_dy * (size * 0.7)
            arrow_length = 10
            
            # Calculate arrowhead tip position first
            arrowhead_tip_x = to_x - unit_dx * arrow_length
            arrowhead_tip_y = to_y - unit_dy * arrow_length
            
            # Line should end where arrowhead starts (back of arrowhead)
            end_x = arrowhead_tip_x - unit_dx * arrow_length * 0.5
            end_y = arrowhead_tip_y - unit_dy * arrow_length * 0.5
            
            # Calculate arrowhead pointing at target
            arrow_x1 = arrowhead_tip_x - arrow_length * (unit_dx * 0.866 - unit_dy * 0.5)
            arrow_y1 = arrowhead_tip_y - arrow_length * (unit_dy * 0.866 + unit_dx * 0.5)
            arrow_x2 = arrowhead_tip_x - arrow_length * (unit_dx * 0.866 + unit_dy * 0.5)
            arrow_y2 = arrowhead_tip_y - arrow_length * (unit_dy * 0.866 - unit_dx * 0.5)
            
            points = f"{int(arrowhead_tip_x)},{int(arrowhead_tip_y)} {int(arrow_x1)},{int(arrow_y1)} {int(arrow_x2)},{int(arrow_y2)}"
            
            return {
                'start_x': start_x,
                'start_y': start_y,
                'end_x': end_x,
                'end_y': end_y,
                'color': troop_arrow['color'],
                'stroke_style': troop_arrow['stroke_style'],
                'points': points
            }
        else:
            # Zero length - return position at source
            return {
                'start_x': from_x,
                'start_y': from_y,
                'end_x': to_x,
                'end_y': to_y,
                'color': troop_arrow['color'],
                'stroke_style': troop_arrow['stroke_style'],
                'points': f"{int(to_x)},{int(to_y)} {int(to_x)},{int(to_y)} {int(to_x)},{int(to_y)}"
            }
    
    def _append_arrow_position(self, x1_values, y1_values, x2_values, y2_values,
                             colors, stroke_styles, opacity_values, arrowhead_points, arrow_pos):
        """Append visible arrow position data"""
        x1_values.append(str(int(arrow_pos['start_x'])))
        y1_values.append(str(int(arrow_pos['start_y'])))
        x2_values.append(str(int(arrow_pos['end_x'])))
        y2_values.append(str(int(arrow_pos['end_y'])))
        colors.append(arrow_pos['color'])
        stroke_styles.append(arrow_pos['stroke_style'])
        opacity_values.append('0.7')
        arrowhead_points.append(arrow_pos['points'])
    
    def _append_last_known_position(self, x1_values, y1_values, x2_values, y2_values,
                                  colors, stroke_styles, opacity_values, arrowhead_points, last_arrow_pos):
        """Append last known position for smooth fade-out"""
        x1_values.append(str(int(last_arrow_pos['start_x'])))
        y1_values.append(str(int(last_arrow_pos['start_y'])))
        x2_values.append(str(int(last_arrow_pos['end_x'])))
        y2_values.append(str(int(last_arrow_pos['end_y'])))
        colors.append(last_arrow_pos['color'])
        stroke_styles.append(last_arrow_pos['stroke_style'])
        opacity_values.append('0')
        arrowhead_points.append(last_arrow_pos['points'])
    
    def _append_fade_out_position(self, x1_values, y1_values, x2_values, y2_values,
                                colors, stroke_styles, opacity_values, arrowhead_points, last_arrow_pos):
        """Append fade-out position when troop loses target"""
        x1_values.append(str(int(last_arrow_pos['start_x'])))
        y1_values.append(str(int(last_arrow_pos['start_y'])))
        x2_values.append(str(int(last_arrow_pos['end_x'])))
        y2_values.append(str(int(last_arrow_pos['end_y'])))
        colors.append(last_arrow_pos['color'])
        stroke_styles.append(last_arrow_pos['stroke_style'])
        opacity_values.append('0')  # Fade out
        arrowhead_points.append(last_arrow_pos['points'])
    
    def _append_hidden_position(self, x1_values, y1_values, x2_values, y2_values,
                              colors, stroke_styles, opacity_values, arrowhead_points):
        """Append hidden position for invisible arrows"""
        x1_values.append('0')
        y1_values.append('0')
        x2_values.append('0')
        y2_values.append('0')
        colors.append('red')
        stroke_styles.append('none')
        opacity_values.append('0')
        arrowhead_points.append('0,0 0,0 0,0')
    
    def _add_arrow_animations_to_elements(self, line, arrowhead, animation_data, frame_duration):
        """Add animation elements to line and arrowhead SVG elements"""
        total_duration = len(self.battlefield.animation_frames) * frame_duration
        
        # Animate arrow positions with smooth transitions
        ET.SubElement(line, 'animate', {
            'attributeName': 'x1',
            'values': ';'.join(animation_data['x1_values']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'linear'
        })
        ET.SubElement(line, 'animate', {
            'attributeName': 'y1',
            'values': ';'.join(animation_data['y1_values']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'linear'
        })
        ET.SubElement(line, 'animate', {
            'attributeName': 'x2',
            'values': ';'.join(animation_data['x2_values']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'linear'
        })
        ET.SubElement(line, 'animate', {
            'attributeName': 'y2',
            'values': ';'.join(animation_data['y2_values']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'linear'
        })        # Animate color and opacity
        ET.SubElement(line, 'animate', {
            'attributeName': 'stroke',
            'values': ';'.join(animation_data['colors']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'discrete'
        })
        ET.SubElement(line, 'animate', {
            'attributeName': 'opacity',
            'values': ';'.join(animation_data['opacity_values']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'discrete'
        })
        
        # Animate stroke style (dotted/solid)
        ET.SubElement(line, 'animate', {
            'attributeName': 'stroke-dasharray',
            'values': ';'.join(animation_data['stroke_styles']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'discrete'
        })
        
        # Animate arrowhead with smooth position transitions
        ET.SubElement(arrowhead, 'animate', {
            'attributeName': 'points',
            'values': ';'.join(animation_data['arrowhead_points']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'linear'
        })
        ET.SubElement(arrowhead, 'animate', {
            'attributeName': 'fill',
            'values': ';'.join(animation_data['colors']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'discrete'
        })
        ET.SubElement(arrowhead, 'animate', {
            'attributeName': 'opacity',
            'values': ';'.join(animation_data['opacity_values']),
            'dur': f'{total_duration}s',
            'repeatCount': 'indefinite',
            'calcMode': 'discrete'
        })
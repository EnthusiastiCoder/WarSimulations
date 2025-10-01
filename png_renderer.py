import os
import datetime
from PIL import Image, ImageDraw

class PNGRenderer:
    """Handles PNG image generation for battlefield frames"""
    
    def __init__(self, battlefield):
        self.battlefield = battlefield
        self.output_folder = None
        self.frames_folder = None
    
    def _ensure_output_folders(self):
        """Create output folders if they don't exist"""
        if self.output_folder is None:
            # Create timestamp-based folder name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_folder = f"battle_simulation_{timestamp}"
            os.makedirs(self.output_folder, exist_ok=True)
            # Create frames subfolder
            self.frames_folder = os.path.join(self.output_folder, "frames")
            os.makedirs(self.frames_folder, exist_ok=True)
    
    def save_board_state(self, scale=20):
        """Save the current board state as a high-quality image"""
        self._ensure_output_folders()
        
        # Create high-resolution image
        img_width = self.battlefield.width * scale
        img_height = self.battlefield.height * scale
        img = Image.new('RGB', (img_width, img_height), '#8B4513') 
        draw = ImageDraw.Draw(img)
        
        # Store arrow data for later drawing
        arrows_to_draw = []
        
        # Collect arrow data first
        for troop in self.battlefield.troops:
            if hasattr(troop, 'target') and troop.target and hasattr(troop, 'action'):
                if troop.action in ['attacking', 'moving', 'waiting']:
                    arrows_to_draw.append({
                        'from_pos': troop.position,
                        'to_pos': troop.target.position,
                        'color': 'red' if troop.action in ['attacking', 'waiting'] else 'yellow',
                        'style': 'dotted' if troop.action == 'waiting' else 'solid'
                    })
        
        # Draw troops
        for troop in self.battlefield.troops:
            self._draw_troop(draw, troop, scale)
        
        # Draw arrows on top of troops
        for arrow in arrows_to_draw:
            self._draw_arrow(draw, arrow, scale)
        
        # Save image
        filename = os.path.join(self.frames_folder, f"frame_{self.battlefield.frame_counter:04d}.png")
        img.save(filename)
        
        return filename
    
    def _draw_troop(self, draw, troop, scale):
        """Draw a single troop with health bar"""
        x, y = troop.position
        x_pixel = x * scale
        y_pixel = y * scale
        
        # Determine color based on team
        color = '#0080FF' if troop.team == 0 else '#FF4040'
        
        # Draw troop shape based on type
        size = int(scale * 0.7)
        
        if troop.attack == 20:  # Barbarian - circle
            draw.ellipse([x_pixel - size//2, y_pixel - size//2, 
                         x_pixel + size//2, y_pixel + size//2], 
                        fill=color, outline='black', width=2)
        else:  # Archer - square
            draw.rectangle([x_pixel - size//2, y_pixel - size//2, 
                           x_pixel + size//2, y_pixel + size//2], 
                          fill=color, outline='black', width=2)
        
        # Draw health bar above troop
        self._draw_health_bar(draw, troop, x_pixel, y_pixel, size, scale)
    
    def _draw_health_bar(self, draw, troop, x_pixel, y_pixel, size, scale):
        """Draw health bar above a troop"""
        bar_width = int(scale * 0.8)
        bar_height = int(scale * 0.15)
        bar_x = x_pixel - bar_width // 2
        bar_y = y_pixel - size // 2 - bar_height - 3
        
        # Background (red for missing health)
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                      fill='red', outline='black', width=1)
        
        # Foreground (green for current health)
        health_ratio = troop.health / troop.max_health
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            draw.rectangle([bar_x, bar_y, bar_x + health_width, bar_y + bar_height], 
                          fill='green', outline=None)
    
    def _draw_arrow(self, draw, arrow, scale):
        """Draw an arrow between two positions"""
        from_x, from_y = arrow['from_pos']
        to_x, to_y = arrow['to_pos']
        
        from_x_pixel = from_x * scale
        from_y_pixel = from_y * scale
        to_x_pixel = to_x * scale
        to_y_pixel = to_y * scale
        
        # Calculate direction for arrow positioning
        dx = to_x_pixel - from_x_pixel
        dy = to_y_pixel - from_y_pixel
        length = (dx*dx + dy*dy)**0.5
        
        if length > 0:
            # Normalize direction
            unit_dx = dx / length
            unit_dy = dy / length
            
            # Offset arrow start and end points to avoid overlap with troops
            size = int(scale * 0.7)
            offset = size + 2
            start_x = from_x_pixel + unit_dx * offset
            start_y = from_y_pixel + unit_dy * offset
            end_x = to_x_pixel - unit_dx * offset
            end_y = to_y_pixel - unit_dy * offset
            
            # Draw arrow line (dotted or solid)
            if arrow['style'] == 'dotted':
                # Draw dotted line by drawing small segments
                line_length = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
                num_dots = int(line_length / 8)  # Dot every 8 pixels
                for i in range(0, num_dots, 2):  # Every other dot for spacing
                    t1 = i / num_dots
                    t2 = min((i + 1) / num_dots, 1.0)
                    x1 = start_x + t1 * (end_x - start_x)
                    y1 = start_y + t1 * (end_y - start_y)
                    x2 = start_x + t2 * (end_x - start_x)
                    y2 = start_y + t2 * (end_y - start_y)
                    draw.line([(x1, y1), (x2, y2)], fill=arrow['color'], width=3)
            else:
                # Draw solid line
                draw.line([(start_x, start_y), (end_x, end_y)], fill=arrow['color'], width=3)
            
            # Draw arrowhead
            arrow_length = 10
            arrow_x1 = end_x - arrow_length * (unit_dx * 0.866 - unit_dy * 0.5)
            arrow_y1 = end_y - arrow_length * (unit_dy * 0.866 + unit_dx * 0.5)
            arrow_x2 = end_x - arrow_length * (unit_dx * 0.866 + unit_dy * 0.5)  
            arrow_y2 = end_y - arrow_length * (unit_dy * 0.866 - unit_dx * 0.5)
            
            draw.polygon([(end_x, end_y), (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)], 
                        fill=arrow['color'], outline=arrow['color'])
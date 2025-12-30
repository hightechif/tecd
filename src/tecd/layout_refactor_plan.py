    def layout(self) -> Layout:
        mode = self.graph.options.get('layout', 'automatic').strip().lower()
        
        if mode == 'vertical':
            return self.rank_layout(direction='vertical')
        elif mode == 'horizontal':
            return self.rank_layout(direction='horizontal')
        else: # automatic
            return self.force_layout(direction='horizontal') # Prefer horizontal flow

    def rank_layout(self, direction='horizontal') -> Layout:
        # ... existing BFS rank logic ...
        
        # In placement loop:
        # if direction == 'horizontal':
        #    x = START + rank * SPACING
        #    y = START + layer * SPACING
        #    rot = 0
        # else:
        #    x = START + layer * SPACING
        #    y = START + rank * SPACING
        #    rot = 90
        pass

    def force_layout(self, direction='horizontal') -> Layout:
        # ... existing force logic ...
        # Update Pinning:
        # If horizontal: Source=(100, CenterY), GND=(Width-100, CenterY)
        # If vertical: Source=(CenterX, 100), GND=(CenterX, Height-100)
        pass

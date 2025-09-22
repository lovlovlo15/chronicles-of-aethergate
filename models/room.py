"""
Room class for Chronicles of Aether Gate
Represents locations in the game world
"""

class Room:
    def __init__(self, room_id, data):
        """Initialize room from JSON data"""
        self.id = room_id
        self.name = data.get("name", "Unknown Room")
        self.description = data.get("description", "An empty room.")
        self.exits = data.get("exits", {})
        self.items = data.get("items", [])
        self.enemy = data.get("enemy", None)
        self.visited = False
        
    def enter(self):
        """Mark room as visited and return description"""
        self.visited = True
        return self.get_description()
    
    def get_description(self):
        """Get full room description with current state"""
        desc = f"**{self.name}**\n\n{self.description}"
        
        if self.items:
            desc += f"\n\nItems here: {', '.join(self.items)}"
        
        if self.enemy:
            desc += f"\n\n⚔️ A {self.enemy} blocks your path!"
        
        exit_list = list(self.exits.keys())
        if exit_list:
            desc += f"\n\nExits: {', '.join(exit_list)}"
        
        return desc
    
    def get_exit(self, direction):
        """Get the room ID for a given exit direction"""
        return self.exits.get(direction.lower())
    
    def take_item(self, item_name):
        """Remove and return item if it exists"""
        if item_name in self.items:
            self.items.remove(item_name)
            return True
        return False
    
    def add_item(self, item_name):
        """Add item to room"""
        if item_name not in self.items:
            self.items.append(item_name)
    
    def clear_enemy(self):
        """Remove enemy (after combat victory)"""
        self.enemy = None
    
    def has_enemy(self):
        """Check if room has an enemy"""
        return self.enemy is not None
    
    def __str__(self):
        return f"{self.name} ({len(self.exits)} exits, {len(self.items)} items)"

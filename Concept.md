# Concept of modified Conways game of life

### **The Endless War: Magicians vs. Goblins**  

#### **Prologue: A Land Once United**  
Long ago, the world of **Eldoria** was a realm of balance, where the **Goblins of the Deepwood** and
the **Magicians of the Ivory Spires** lived in harmony. Though different in nature, they coexisted,
each thriving in their own ways. Goblins, cunning and industrious, were expert builders,
crafting sprawling underground cities and vast forest strongholds. Magicians, 
wise and disciplined, devoted themselves to the study of the arcane, harnessing 
the energies of the world to shape reality itself.  

Trade flourished between the two civilizations. The goblins provided raw materials 
from deep within the earth, while the magicians wove spells to enhance 
their tools and fortifications. There was an unspoken understanding: magic 
was not to be used against the goblins, and goblins were not to encroach upon the sanctuaries 
of the magicians. For centuries, this delicate balance remained intact.  

#### **The Catalyst of War**  

But peace is fragile. A single moment can shatter it forever.  

No one knows exactly **who struck first**—the goblins say it was the magicians, and the magicians swear it was 
the goblins. Some claim it was an accident, others whisper of a darker force manipulating both sides.  

One fateful night, in the valley between their lands, an ancient **artifact of power** was 
unearthed by goblin miners. The artifact, pulsing with raw energy, caught the attention of 
the magicians, who immediately recognized its **dangerous potential**. They demanded that 
it be handed over, claiming only their wisdom could contain its destructive force. But the 
goblins refused, believing it to be their rightful discovery—one that could elevate their 
civilization beyond the shadow of magic.  

A tense negotiation escalated into a **dispute**. The first **spell was cast**. The first **blade was drawn**.  

The artifact, reacting to the surge of emotions and violence around it, unleashed 
an **unstoppable curse upon the land**. Time fractured. The very essence of life became locked 
in an **eternal cycle of death and rebirth**, trapping magicians and goblins in a never-ending 
struggle. No matter how many times one side gained the upper hand, the battlefield would 
reset, their fallen reborn anew.  

#### **The Cursed Cycle**  

Now, the war never ends.  
Magicians and goblins continue to clash across the landscape, bound by a force beyond 
their understanding. Each battlefront is shaped by its surroundings:  

- The **Goblin Strongholds**, where their numbers swell like a tide.  
- The **Sanctuaries of Sorcery**, where magic weaves reality in favor of the arcane.  
- The **Valley of eternal peace**, remnants of the world before the war, where some still remember what was lost.  
- The **Cemetery of Ash**, where neither side can gain a foothold, and only the strongest survive.  

Despite the endless bloodshed, both sides still seek a way to **break the cycle**, to 
**undo the curse**, to **remember what peace felt like**. But until that day comes—if it ever does—the war rages on.  

For **goblins** and **magicians**, there is no future.  
Only the battle.  
Only survival.  

_**And so, the war continues…**_

## Rules of the Game

### Basic Growth Rules (Modified from Conway's Life)

Actually in our game there will be 3 types of cells:

1. Empty cell with nothing. Can be shown as grass image or just make it green for visual appearance. It is populate by other 2 types of cells 
2. Goblic cell
3. Magician cell 

- A goblin/magician cell survives if it has 2 or 3 neighbors of its kind.
- A goblin/magician cell dies from loneliness if it has 0 or 1 neighbors.
- A goblin/magician cell dies from overcrowding if it has 4 or more neighbors.
- An empty cell spawns a goblin or magician if it has exactly 3 neighbors of that type

### Special combat rules 

If a goblin and a magician encounters each other apply these rules:

- If magicians and goblins try to expand on the same cell, don't populate it with either of the mobs on that iteration
- If rival cells are near each other then leave the one with more allies.
- If number of the allies equal then leave them as they are.

### Special zones rules

#### Goblin stronghold

- Goblins have stronger reproduction rates (can spawn with just 2 neighbors instead of 3).
- Magicians weakened (struggle to survive without 3+ magician neighbors).

#### Magician base

- Magicians more resilient (can survive overcrowding up to 5 neighbors).
- Goblins struggle to spread (need 4 goblin neighbors to reproduce instead of 3).

#### Peaceful place (Valley of Eternal Peace)

A place of peaceful existence with the following rule:

- Combat rules does not apply
- Apply basic rules of game of life, but with following modifications:
    - A random mob appears in the cell if it is surrounded by 3 alive cells (type of mob doesn't matter)
    - A random mob dies if surrounded by <2 alive cells (type of mob doesn't matter)
    - A random mob stays in the cell if it is surrounded by 2-3 alive cells (type of mob doesn't matter)
    - A random mob dies due to overpopulation if it is surrounded by >4 alive cells (type of mob doesn't matter)


#### Deadly place (Cementery of ash)

- Cells die if they have <3 neighbors.

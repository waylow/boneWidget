# Bone Widget

2.7 explanation : https://vimeo.com/184159913

### To do:
- Add documentation with images in the readme file
- Where has the 'hide collection' operator gone
- make the 'symmetrize widget' operator check if the bone/widget has a mirrored side first before doing anything else.  At the moment it will create the collection if it doesn't exist (this is new issue because I let the user edit an existing widget that isn't in the default location - if the widget already existed that is)
-if the collection is disabled, it will throw an error when you try to add or edit etc

- the "select object as widget" should also match the transforms after creation
- let the user change the widget suffix to a prefix for a different naming convention
- extract and edit a widget?  Say you're editing a rig that doesn't have mesh objects for the widgets in the file (only mesh data).
Maybe there can be a way of extracting them and making them real objects.
- The match Bone Transforms does not work well when the bone scale is not at 1.0


## v1.8 Release Notes:
* Fix: updated to work with Blender 2.93/3.0
* Functionality change: If you are editing a Widget that already exists, it now will use the collection where it is actually located rather than trying to find it in the user preferences settings (fixes error if the collection was called something different)
* changed the default collection name and widget names to better match with Rigify (not my preferred naming convention but its better to have more consistency)
* Removed PayPal funding links
* Removed Logger
* Fix: If collection is 'excluded' in the outliner it now re-enables it

### Edited Widgets
* Resized '3 Axes' widget to better match a default size of 1 blender unit (and sits over the 6 axes nicely)
* Renamed 'FK_Limb' to 'FK Limb 1'
* Renamed 'Arm' widget to 'FK Limb 2'
* Renamed widgets to exclude the underscore (for consistency)
* Lowered the resolution of the 'Chest' widget (makes it difficult to edit when it was so high poly). Resized it to 1 blender unit in the Y and aligned it to the +y axis by default
* lowered the resolution of "Arrow Double Curved"
* added a thicker version if the arrow called "Roll 3"
* lowered the resolution of "Torso"
* Added "Torso 1" shape
* Aligned "Eye Target" to the Y axis, renamed to "Eye Target 1", resized.
* Added "Eye Target 2" shape
* Straightened the "Clavicle" shape (makes it more flexible)
* Gear Complex/Gear Simple - aligned to world space
* Rename Finger to "Paddle (square)"
* Added a variation of "Paddle (rounded)" with a round end
* Aligned "Plane" with the Y axis (will 'slide' in a logical direction out of the box)
* added a "Plane (rounded)" which has rounded corners
* Rotated "Roll" slightly so it looks symmetrical, Renamed to "Roll 1"
* Added "Roll 2"
* Added "Arrow Single Straight" and "Arrow Double Straight"
* Added "Saddle" shape - useful for chests and head controls as a starting point
* Added "Rhomboid" shape
* flipped "Arrow Head" and renamed to "Pyramid"


## v1.7 Release Notes
* Fix: Allow rename of Addons-Folder
* Fix: Fixed the symmetrize error if the .L or the .R didn't have a widget
* Fix: Symmetrize Operator caused Error when clicking in Object mode
* Fix: Return to Armature: Didn't unselect widget-object before returning to armature
* Fix: Edit Widget: Show only if active bone has a widget
* Feature: Widgets renamed: Gear --> Gear_complex, Root --> Root_1
* Feature: New Widgets: 3 Axes, 6 Axes, Arrow_double_sided, Arrow_head, Chest, Clavicle, Eyes_Target, FK_Limb, Gear_simple,
Roll, Root_2, Torso
* Feature: New Property: Panel Category
* Feature: New Property: Bone Widget symmetry suffix
* Feature: Add selected Mesh as widget-shape
* Feature: Added Logger


## v1.6 Release Notes
* Fixed the "DELETE UNUSED WIDGETS" function (was crashing because the context was wrong)


## v1.5 Release notes
* fixed the symmetrize error if the .L and .R were sharing the same shape and you tried to symmetrize


## v1.4 Release notes
* add function to clear widget from bone
* add operator to show/hide the collections
* add operator that will resync the names of the wdgts to the bones
* add operator to delete unused widgets
* add property to be able to rotate the widgets
* improve the ui
* add some default widgets (line, cube, half cube, circle, gear, triangle)
* fixed bug when 'custom bone transform' is enabled, size is incorrect

## v1.3 Release Notes:
* updated to work with latest 2.8 api
* added user preferences for the widget prefix and the collection name
* doesn't delete old widget when replacing with a new version [resolved]
* it will only match the bone matrix when the armature is at a scale of 1.0  This is because the old id_data used to point to the object, but now it points to the data object. [resolved]
* also doesn't match bone transforms if armature not at 0,0,0 [resolved]
* doesn't work correctly when there is a "custom shape transforms" [resolved]
* match Bone Transforms works when bone is selected but not when the widget is selected [resolved]
* if the widget names end with .001 etc it will throw an error [resolved]
* if no objects are selected it will throw an error [resolved]

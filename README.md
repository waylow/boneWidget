# Bone Widget

Video explanation:
https://www.youtube.com/watch?v=PDNVeDOzjzw

## Description:
Bone Widget is a blender add-on to assist with making custom bone shapes. It has an editable library of shapes that make it easy to apply to any rig.

It ships with many shapes pre-made but you can also add your own to the library to make rigging easier.

## Installation:

1. Download the zipped code here from Github. (Check in the release tab for the latest stable release)
2. In Blender, open Preferences->Addons->Install. Navigate to where you saved the zip file and click install.
3. Enable the Addon with the checkbox.
4. The UI will appear in the properties panel (n panel) in the 3d viewport.

## UI Panel

<img src="images/bone_widget_UI.png" alt="drawing" width="700"/>

### Preview Panel Checkbox:
This will show/hide the large widget preview panel. It's also possible to set your preferred option for this in the preferences. (The default is enabled)

### Preview Panel:
This is the large preview panel that displays the currently selected widget.  Click on this panel to open the selection menu.

### Shape Drop Down:
This is the active shape from Bone Widget Library.

## BW Specials Menu:




### Add to Widget library

To add a mesh object to the library, select a mesh object and click this button.
Give the mesh object an appropriate name and then confirm.  Your widget will be added to the library.
(User widgets are stored in a separate json file to the shapes that come with the addon.)

### Remove from Widget Library

This will remove the active shape from the library.
Select the shape you want to remove from the list.  And click this. Boom, it is gone (forever!).
This will work on any widget in the list.


## Creating a Widget:


### Create:
Select a bone (or bones), choose the shape from the drop down menu, then press create.
This will create a widget object for each of the selected bones.  The widget objects will be placed in the collection that is specified in the user preferences.


### Redo panel

<img src="images/bone_widget_redo_panel_advanced.png" alt="drawing" width="400">


#### Scale to bone length:
When enabled the Global Size will be multiplied by the bone length.  (ie - the widget  will be relative size to the size of the bone)
With this disabled, the Global Size will be in Blender units.

#### Use Face Data:
If the widget that has been added has faces, you can choose to show them with this setting.  This will either include or exclude them when the widget is built.

#### Global size:
This will be the size of the widget, relative to the size of the bone if 'Scale to bone length' is enabled.  Or in Blender units if that setting is disabled.

#### Global Size XYZ: (Advanced Option only)
When the advanced options is enabled you can access the individual scale channels of the created widget, rather that 1 scale value for all 3 axes

#### Slide:
This will slide the position of the widget along the Y axis (or length) of the bone.  0.0 is at the head of the bone and 1.0 is the tail.  (negative values are possible too)


#### Slide X/Y/Z (Advanced Option Only)
When advanced mode is enabled, the slide property is split into 3 axies rather than just the defalt y axis.

#### Rotation X/Y/Z
You can rotate the widget by these values at the time of creation.  This can save you from having to jump into edit mode to rotate a widget to better align with your situation.

#### Wire Width:
This will let you set the wireframe thickness.  The default setting is 2.0 but Blender will allow any float between 1 and 16. 

#### Advanced Options:
This checkbox will switch the slide value into 3 axes rather than just the default Y axis.  This will enable the user to position the widget in some situations without having to jump into edit mode.


### Edit/To Bone:
When in pose mode, this will jump into edit mode for the custom bone shape and allow you to edit it.
When you have the shape selected (object or edit mode), this button will display as "To Bone".  That will take you back to pose mode, if that mesh object is in face a custom shape.

<b>Note on Creating and Editing Shapes:</b><br>
When you 'Create' a shape, it will always be placed in the collection set in the user preferences.<br>
If you 'Edit' a shape, it will stay in whatever collection that widget was already located.


### Match bone Transforms:
If the widgets get out of alignment with the location of the bone itself, this operator will snap the selected widget to the matrix of the bone.  It works if you have the bone(s) selected or if you have the widget object(s) selected.

#### Resync Widget Names:
Sometimes you might rename a bone/or a widget.  This operator will loop through all the custom bone shapes and make sure they match the name of the bone they are assigned to.

<b>Note:</b>
Currently the add-on is designed to have one widget per bone, if you have multiple users of the same widget, it will be renamed to the last user it finds.

### Clear Bone Widget:
This will clear the custom bone shapes from all the selected bones.

### Delete Unused Widgets:
This operator will loop through the widget collection and delete anything that isn't being used.  This helps keep things tidy.

### Use Selected Object:
If you want to apply a mesh object that is already in your scene as a custom shape, you can use this option.
First select the mesh shape you want to use (object mode), then shift select the armature, switch into pose mode and make sure you select any bone(s) you want this shape to be applied to.  Then press the button.


### Hide/Show Collection:
As the name would suggest this will toggle the visibility of the widget collection.  

<blockquote>
<b>Note:</b>
This will only toggle the visibility of the designated widget collection (set in the preferences).  If your character has widgets outside of this collection, it will not toggle the visibilty of that.
</blockquote>
</br></br>

---
---
## v2.1 Release Notes:
- [Added] Markus Berg added functionality to display images of the widgets. What a flippin' legend.
- [Added] Markus split the scale and slide into 3 axies and implemented toggle to show simple/advanced mode
- [Added] Popup added for name input when adding a widget to the library
- [Added] import/export user library of shapes
- [Added] popup to name the widget when adding to library
- [Added] you can now add custom images to the widgets (or use the in-built image place holders)
- [Added] added wire width option when the widgets are created
- [change] remove the "_old" functionality of the code (just delete the old widget)
- [fix] the match bone transforms now takes the custom shape transforms into account
- [fix] if the collection didn't exist when you tried to delete unused widgets it would throw an error.  You now get a message that hints at the problem.
 - [fixed] If there is no active object the panel.py would throw an error
- [fixed] If you Symmetrized the Shape in pose mode with no widget added, it will throw an error.

## v2.0 Release Notes:
- changed the default name of the n panel to 'Rigging' rather than 'Rig Tools'
- [fixed Bug] if the bone was using an override transform, it will use this bone mirror the widget to rather than just taking that bone's matrix
- [Enhancement] Added setting in the user preferences so it can optionally use the Rigify naming convention for widget creation (collection and widget names).

## v1.9 Release Notes:
- [Fix] widget collection no longer needs to be in the master scene for the addon to find it.
- [Fix] All the related functions now search for the collection recursively so the structure of the Widget Collection location doesn't matter.
- [Fix] change the mirrorShape function to only display in pose mode to avoid errors.

## v1.8 Release Notes:
* Fix: updated to work with Blender 2.93/3.0
* Functionality change: If you are editing a Widget that already exists, it now will use the collection where it is actually located rather than trying to find it in the user preferences settings (fixes error if the collection was called something different)
* changed the default collection name and widget names to better match with Rigify (not my preferred naming convention but its better to have more consistency)
* Removed PayPal funding links
* Removed Logger
* Functionality change: I rewrote the way to add the selected object as a widget without having to read and write to a text file
* Fix: If collection is 'excluded' in the outliner it now re-enables it.

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

### Widget Edits (from v1.7)
* Resized '3 Axes' widget to better match a default size of 1 blender unit (and sits over the 6 axes nicely)
* Renamed 'FK_Limb' to 'FK Limb 1'
* Renamed 'Arm' widget to 'FK Limb 2'
* Renamed widgets to exclude the underscore (for consistency)
* Lowered the resolution of the 'Chest' widget (makes it difficult to edit when it was so high poly). Resized it to 1 blender unit in the Y and aligned it to the +y axis by default
* Lowered the resolution of "Arrow Double Curved"
* Added a thicker version if the arrow called "Roll 3"
* Lowered the resolution of "Torso"
* Added "Torso 1" shape
* Aligned "Eye Target" to the Y axis, renamed to "Eye Target 1", resized.
* Added "Eye Target 2" shape
* Straightened the "Clavicle" shape (makes it more flexible)
* Gear Complex/Gear Simple - aligned to world space
* Rename Finger to "Paddle (square)"
* Added a variation of "Paddle (rounded)" with a round end
* Aligned "Plane" with the Y axis (will 'slide' in a logical direction out of the box)
* Added a "Plane (rounded)" which has rounded corners
* Rotated "Roll" slightly so it looks symmetrical, Renamed to "Roll 1"
* Added "Roll 2"
* Added "Arrow Single Straight" and "Arrow Double Straight"
* Added "Saddle" shape - useful for chests and head controls as a starting point
* Added "Rhomboid" shape
* Flipped "Arrow Head" and renamed to "Pyramid"


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

# boneWidget

2.7 explanation : https://vimeo.com/184159913

----------
Current Bugs:
-CRASH "DELETE UNUSED WIDGETS" is used
-fails if the bone has a custom transform shape

v1.5 Release notes
-fixed the symmetrize error if the .L and .R were sharing the same shape and you tried to symmetrize

v1.4 Release notes
-add function to clear widget from bone [DONE]
-add operator to show/hide the collections [DONE]
-add operator that will resync the names of the wdgts to the bones [DONE]
-add operator to delete unused widgets [DONE]
-add property to be able to rotate the widgets [DONE]
-improve the ui [Done]
-add some default widgets (line, cube, half cube, circle, gear, triangle) [DONE]
-fixed bug when 'custom bone transform' is enabled, size is incorrect [DONE]



v1.3 Release Notes:
-updated to work with latest 2.8 api
-added user preferences for the widget prefix and the collection name
Resolved issues:
-doesn't delete old widget when replacing with a new version [resolved]
-it will only match the bone matrix when the armature is at a scale of 1.0  This is because the old id_data used to point to the object, but now it points to the data object. [resolved]
-also doesn't match bone transforms if armature not at 0,0,0 [resolved]
-doesn't work correctly when there is a "custom shape transforms" [resolved]
-match Bone Transforms works when bone is selected but not when the widget is selected [resolved]

Symmetrize errors:
  -if the widget names end with .001 etc it will throw an error [resolved]
  -if no objects are selected it will throw an error [resolved]

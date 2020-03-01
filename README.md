# boneWidget

2.7 explanation : https://vimeo.com/184159913

----------
2.8 list of bugs/todos:

-doesn't delete old widget when replacing with a new version [DONE]

Symmetrize errors:
-if the widget names end with .001 etc it will throw an error [resolved]
-if no objects are selected it will throw an error [resolved]

General errors:
-at the moment it will only match the bone matrix when the armature is at a scale of 1.0  This is because the old id_data used to point to the object, but now it points to the data object. [SOLVED]
-also doesn't match bone transforms if armature not at 0,0,0 [SOLVED]

-doesn't work correctly when there is a "custom shape transforms" [resolved]

-match Bone Transforms works when bone is selected but not when the widget is selected [resolved]

Future stuff:
-add function to clear widget from bone [DONE]
-add operator to show/hide the collections [DONE]
-add operator that will resync the names of the wdgts to the bones [DONE]
-add operator to delete unused widgets [DONE]
-add property to be able to rotate the widgets [DONE]

-improve the ui [Done]

-add some default widgets
    -line, cube, plane, half cube, circle, gear, triangle

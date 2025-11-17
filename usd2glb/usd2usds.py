
import bpy
import os

def export_objects_as_usd(output_dir):
    """
    Exports each object in the current scene as a separate USD file.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the current scene
    scene = bpy.context.scene

    # Iterate over all objects in the scene
    for obj in scene.objects:
        # Ensure the object is a mesh (or other type you want to export)
        if obj.type == 'MESH':
            # Select the object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            # Define output path for each object
            object_name = obj.name
            output_path = os.path.join(os.path.join(output_dir, obj.name), f"{object_name}.usd")

            # Export the object to USD
            bpy.ops.wm.usd_export(filepath=output_path, selected_objects_only=True)
            print(f"Exported {object_name} to {output_path}")


def main():
    output_directory = 'path/to/your/directory'
    export_objects_as_usd(output_directory)

if __name__ == "__main__":
    main()

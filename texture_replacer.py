from pygltflib import GLTF2
import json
import os
import argparse
from pathlib import Path
import shutil

def replace_textures(original_glb, texture_dir, output_glb):
    """Replace textures in a GLB file with extracted ones"""
    
    # Load the texture mapping log
    log_path = os.path.join(texture_dir, 'texture_mapping.json')
    if not os.path.exists(log_path):
        raise ValueError("Texture mapping log not found. Please extract textures first.")
    
    with open(log_path, 'r') as f:
        texture_log = json.load(f)
    
    # Create a copy of the original GLB
    shutil.copy2(original_glb, output_glb)
    
    # Load the GLB file
    gltf = GLTF2.load(output_glb)
    
    # Process each texture in the log
    for texture_info in texture_log:
        index = texture_info['index']
        texture_path = texture_info['extracted_path']
        
        if not os.path.exists(texture_path):
            print(f"Warning: Texture file not found: {texture_path}")
            continue
        
        # Read the new texture file
        with open(texture_path, 'rb') as f:
            new_texture_data = f.read()
        
        # Get the buffer view for this image
        buffer_view = gltf.bufferViews[gltf.images[index].bufferView]
        
        # Calculate padding to maintain 4-byte alignment
        padding_bytes = (4 - (len(new_texture_data) % 4)) % 4
        padded_data = new_texture_data + (b'\x00' * padding_bytes)
        
        # Update the buffer view
        buffer_view.byteLength = len(padded_data)
        
        # Replace the data in the binary blob
        old_blob = gltf.binary_blob()
        new_blob = (
            old_blob[:buffer_view.byteOffset] +
            padded_data +
            old_blob[buffer_view.byteOffset + buffer_view.byteLength:]
        )
        
        # Update the GLB with the new binary blob
        gltf.set_binary_blob(new_blob)
    
    # Save the modified GLB
    gltf.save(output_glb)
    print(f"Created new GLB with replaced textures: {output_glb}")

def main():
    parser = argparse.ArgumentParser(description='Replace textures in a GLB file')
    parser.add_argument('glb_file', type=str, help='Path to input GLB file')
    parser.add_argument('texture_dir', type=str, help='Directory containing extracted textures')
    parser.add_argument('--output', '-o', type=str, help='Output GLB file (defaults to input_modified.glb)')
    
    args = parser.parse_args()
    
    # Convert paths to absolute paths
    glb_path = Path(args.glb_file).resolve()
    texture_dir = Path(args.texture_dir).resolve()
    
    if not args.output:
        output_path = glb_path.parent / f"{glb_path.stem}_modified{glb_path.suffix}"
    else:
        output_path = Path(args.output).resolve()
    
    if not glb_path.exists():
        print(f"Error: GLB file not found: {glb_path}")
        return
    
    if not texture_dir.exists():
        print(f"Error: Texture directory not found: {texture_dir}")
        return
    
    print(f"Processing GLB file: {glb_path}")
    print(f"Using textures from: {texture_dir}")
    print(f"Output file: {output_path}")
    
    try:
        replace_textures(str(glb_path), str(texture_dir), str(output_path))
    except Exception as e:
        print(f"Error replacing textures: {e}")

if __name__ == "__main__":
    main() 
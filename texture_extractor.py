from pygltflib import GLTF2
import base64
import os
import argparse
from pathlib import Path
import json

def get_texture_role(gltf, image_index):
    """Determine the role of a texture by checking material references"""
    roles = []
    
    # Check all materials for references to this image
    for material in gltf.materials:
        pbr = material.pbrMetallicRoughness
        
        # Check base color texture
        if hasattr(pbr, 'baseColorTexture') and pbr.baseColorTexture:
            if gltf.textures[pbr.baseColorTexture.index].source == image_index:
                roles.append('baseColor')
        
        # Check metallic roughness texture
        if hasattr(pbr, 'metallicRoughnessTexture') and pbr.metallicRoughnessTexture:
            if gltf.textures[pbr.metallicRoughnessTexture.index].source == image_index:
                roles.append('metallicRoughness')
        
        # Check normal texture
        if hasattr(material, 'normalTexture') and material.normalTexture:
            if gltf.textures[material.normalTexture.index].source == image_index:
                roles.append('normal')
        
        # Check occlusion texture
        if hasattr(material, 'occlusionTexture') and material.occlusionTexture:
            if gltf.textures[material.occlusionTexture.index].source == image_index:
                roles.append('occlusion')
        
        # Check emissive texture
        if hasattr(material, 'emissiveTexture') and material.emissiveTexture:
            if gltf.textures[material.emissiveTexture.index].source == image_index:
                roles.append('emissive')
    
    return '_'.join(roles) if roles else 'unknown'

def extract_textures(glb_path, output_dir, naming_scheme='original'):
    # Load the GLB file
    gltf = GLTF2.load(glb_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if there are any textures
    if not gltf.bufferViews or not gltf.images:
        print("No textures found in the GLB file.")
        return
    
    # Create a log of extracted textures
    texture_log = []
    
    # Process each image in the GLB
    for i, image in enumerate(gltf.images):
        # Get the bufferview that contains the image data
        buffer_view = gltf.bufferViews[image.bufferView]
        
        # Get the binary data
        data = gltf.binary_blob()[buffer_view.byteOffset:buffer_view.byteOffset + buffer_view.byteLength]
        
        # Determine file extension from MIME type
        extension = image.mimeType.split('/')[-1]
        
        # Generate filename based on naming scheme
        if naming_scheme == 'role':
            role = get_texture_role(gltf, i)
            base_name = f"{role}_{i}" if role != 'unknown' else f"texture_{i}"
            filename = f"{base_name}.{extension}"
        elif naming_scheme == 'original':
            if hasattr(image, 'name') and image.name:
                # Clean the filename to remove any invalid characters
                base_name = "".join(c for c in image.name if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{base_name}.{extension}"
            else:
                filename = f"texture_{i}.{extension}"
        else:  # index
            filename = f"texture_{i}.{extension}"
            
        output_path = os.path.join(output_dir, filename)
        
        # If file already exists, add a number to prevent overwriting
        counter = 1
        while os.path.exists(output_path):
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{counter}{ext}"
            output_path = os.path.join(output_dir, filename)
            counter += 1
        
        # Save the texture
        with open(output_path, 'wb') as f:
            f.write(data)
        
        # Log the extraction details
        texture_log.append({
            'index': i,
            'original_name': image.name if hasattr(image, 'name') and image.name else None,
            'mime_type': image.mimeType,
            'extracted_path': output_path,
            'role': get_texture_role(gltf, i) if naming_scheme == 'role' else None
        })
        
        print(f"Saved texture: {filename}")
    
    # Save the texture log
    log_path = os.path.join(output_dir, 'texture_mapping.json')
    with open(log_path, 'w') as f:
        json.dump(texture_log, f, indent=2)
    
    return texture_log

def main():
    parser = argparse.ArgumentParser(description='Extract textures from GLB file')
    parser.add_argument('glb_file', type=str, help='Path to input GLB file')
    parser.add_argument('--output', '-o', type=str, default='extracted_textures',
                       help='Output directory for extracted textures')
    parser.add_argument('--naming', '-n', type=str, choices=['index', 'original', 'role'],
                       default='original', help='Naming scheme for extracted textures')
    
    args = parser.parse_args()
    
    # Convert paths to absolute paths
    glb_path = Path(args.glb_file).resolve()
    output_dir = Path(args.output).resolve()
    
    if not glb_path.exists():
        print(f"Error: GLB file not found: {glb_path}")
        return
    
    print(f"Processing GLB file: {glb_path}")
    print(f"Output directory: {output_dir}")
    print(f"Using naming scheme: {args.naming}")
    
    extract_textures(str(glb_path), str(output_dir), args.naming)

if __name__ == "__main__":
    main() 
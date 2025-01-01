## Installation

1. Clone this repository or download the script files
2. Install the required packages using one of these methods:

   ```bash
   # Method 1: Using requirements.txt
   pip install -r requirements.txt
   
   # Method 2: Direct installation
   pip install pygltflib
   ```
## Basic Usage
python texture_extractor.py model.glb
or
python texture_extractor.py model.glb -o output_dir -n role
### Command Line Arguments

- `glb_file`: Path to the input GLB file (required)
- `--output` or `-o`: Output directory for extracted textures (optional, defaults to 'extracted_textures')
- `--naming` or `-n`: Naming scheme for extracted textures (optional, defaults to 'original')
  - `original`: Use original filenames from the GLB when available
  - `index`: Simple numbered naming (texture_0.png, texture_1.jpg, etc.)
  - `role`: Name files based on their material role (baseColor, normal, metallicRoughness, etc.)

## Output

The script will:
- Create the output directory if it doesn't exist
- Extract all textures found in the GLB file
- Save them as separate files named `texture_0.png`, `texture_1.jpg`, etc. (extension based on original format)
- Print progress information during extraction

## Error Handling

The script includes error handling for:
- Missing input files
- GLB files without textures
- Invalid file paths

## Texture Replacement

After extracting textures, you can replace them in the original GLB file:

```bash
python texture_replacer.py original.glb extracted_textures
```

Or specify a custom output file:
```bash
python texture_replacer.py original.glb extracted_textures -o modified.glb
```

The texture replacer will:
1. Create a copy of the original GLB
2. Replace each texture with its corresponding extracted version
3. Maintain the original texture references and material properties
4. Save the modified GLB to a new file

### Important Notes
- The texture replacer requires the texture mapping log created during extraction
- Each texture must maintain the same format as the original
- The script will preserve all material properties and texture references
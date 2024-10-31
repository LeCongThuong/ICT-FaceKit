import open3d as o3d
import numpy as np
import json
import argparse
import openmesh as om

def load_json_indices(json_path):
    """Load vertex indices from a JSON file."""
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    return json_data['idx_to_landmark_verts']

def load_mesh_vertices(obj_path):
    """Load mesh vertices from an OBJ file using OpenMesh."""
    # Read the mesh using OpenMesh
    mesh = om.read_trimesh(obj_path)

    # Extract vertices and convert to a NumPy array
    vertices = np.array([mesh.point(vh) for vh in mesh.vertices()], dtype=np.float64)
    
    return vertices

def extract_and_save_vertices(vertices, vertex_indices, output_path):
    """Extract vertices from a given list of indices and save to a .npy file."""
    # Extract indices starting from index 17
    vertex_indices = vertex_indices[17:]
    extracted_vertices = vertices[vertex_indices]
    
    # Ensure the shape is (Number of vertices, 3)
    print("Extracted vertices shape:", extracted_vertices.shape)
    
    # Save to a .npy file
    np.save(output_path, extracted_vertices)
    print(f"Vertices extracted and saved successfully as {output_path}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Extract vertices from OBJ and save to .npy.")
    parser.add_argument('--obj_path', type=str, required=True, help="Path to the input OBJ file.")
    parser.add_argument('--json_path', type=str, required=True, help="Path to the JSON file containing vertex indices.")
    parser.add_argument('--output_path', type=str, default='extracted_vertices.npy', help="Path to save the extracted .npy file.")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Load indices and vertices
    vertex_indices = load_json_indices(args.json_path)
    vertices = load_mesh_vertices(args.obj_path)
    print(vertices.shape)
    # Extract and save vertices
    extract_and_save_vertices(vertices, vertex_indices, args.output_path)

if __name__ == "__main__":
    main()

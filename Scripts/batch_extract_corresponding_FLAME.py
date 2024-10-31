import openmesh as om
import os
import sys
import numpy as np
import argparse
import open3d as o3d
from tqdm import tqdm


def parse_arguments():
    # Add argparse to handle input arguments
    parser = argparse.ArgumentParser(description="Extract, visualize, and save mesh of specific parts of 3D models in a directory.")
    parser.add_argument("--input_dir", type=str, required=True, help="Path to the input directory containing .obj files")
    parser.add_argument("--output_dir", type=str, required=True, help="Path to the output directory to save the extracted meshes")
    return parser.parse_args()

def load_mesh(file_path):
    # Load 3D model using OpenMesh
    mesh = om.read_trimesh(file_path)
    # Check if mesh was successfully loaded
    if mesh.n_vertices() == 0:
        raise ValueError(f"Failed to load the mesh from {file_path}. Please check the file path and ensure the file is valid.")
    return mesh

def extract_mesh(mesh):
    # List of parts with vertex indices for extraction
    table_parts = {
        "Face": [0, 9408],
        "Head and Neck": [9409, 11247],
        "Eye socket left": [13294, 13677],
        "Eye socket right": [13678, 14061],
        "Eyeball left": [21451, 23020],
        "Eyeball right": [23021, 24590],
        "Lacrimal fluid left": [24591, 24794],
        "Lacrimal fluid right": [24795, 24998],
        "Eye blend left": [24999, 25022],
        "Eye blend right": [25023, 25046]
    }

    included_vertex_indices = set()
    for vertex_indices in table_parts.values():
        included_vertex_indices.update(range(vertex_indices[0], vertex_indices[1] + 1))

    # Filter faces containing all vertices within selected parts
    faces = []
    for face in mesh.face_vertex_indices():
        if all(vertex in included_vertex_indices for vertex in face):
            faces.append(face)

    vertices = mesh.points()
    # Keep only vertices used in faces
    unique_vertex_indices = np.unique(np.array(faces).flatten())
    vertices = vertices[unique_vertex_indices]
    faces = [[np.where(unique_vertex_indices == v)[0][0] for v in face] for face in faces]

    return vertices, np.array(faces)

def create_open3d_mesh(vertices, faces):
    # Convert vertex and face lists to Open3D TriangleMesh
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    mesh.compute_vertex_normals()
    return mesh

def save_mesh(mesh, output_path):
    # Save mesh to file (.ply or .obj)
    print(f"Saving mesh to {output_path}")
    o3d.io.write_triangle_mesh(output_path, mesh, write_vertex_normals=False)

def process_directory(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all .obj files in the input directory
    for file_name in tqdm(os.listdir(input_dir)):
        if file_name.endswith(".obj"):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, file_name)

            try:
                mesh = load_mesh(input_path)
                vertices, faces = extract_mesh(mesh)
                new_mesh = create_open3d_mesh(vertices, faces)
                save_mesh(new_mesh, output_path)
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

def main():
    args = parse_arguments()
    process_directory(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()

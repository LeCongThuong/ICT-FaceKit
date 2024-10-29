import openmesh as om
import sys
import numpy as np
import argparse
import open3d as o3d

def parse_arguments():
    # Thêm argparse để xử lý tham số đầu vào
    parser = argparse.ArgumentParser(description="Extract, visualize, and save mesh of specific parts of the 3D model.")
    parser.add_argument("--file", type=str, required=True, help="Path to the 3D model file (.obj)")
    parser.add_argument("--output", type=str, required=True, help="Path to save the extracted mesh (.obj)")
    parser.add_argument("--mtl", type=str, help="Path to the material file (.mtl) for .obj output")
    return parser.parse_args()

def load_mesh(file_path):
    # Tải mô hình 3D bằng OpenMesh
    mesh = om.read_trimesh(file_path)
    # Kiểm tra nếu mesh đã được tải thành công
    if mesh.n_vertices() == 0:
        raise ValueError("Failed to load the mesh. Please check the file path and ensure the file is valid.")
    return mesh

def extract_mesh(mesh):
    # Danh sách các bộ phận với vertex indices chỉ chứa những phần có "x"
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

    # Lọc các mặt chứa tất cả các đỉnh thuộc các phần được chọn
    faces = []
    for face in mesh.face_vertex_indices():
        if all(vertex in included_vertex_indices for vertex in face):
            faces.append(face)

    vertices = mesh.points()
    # Chỉ giữ lại các đỉnh được sử dụng trong các mặt
    unique_vertex_indices = np.unique(np.array(faces).flatten())
    vertices = vertices[unique_vertex_indices]
    faces = [[np.where(unique_vertex_indices == v)[0][0] for v in face] for face in faces]

    return vertices, np.array(faces), unique_vertex_indices

def create_open3d_mesh(vertices, faces):
    # Chuyển đổi danh sách đỉnh và mặt thành Open3D TriangleMesh
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    if len(vertices) > 0 and len(faces) > 0:
        mesh.compute_vertex_normals()
    return mesh

def save_mesh(mesh, output_path, vertices, faces, unique_vertex_indices, mtl_path=None):
    # Lưu mesh thành tệp .obj với mtl, v, vn, vt, f
    print(f"Saving mesh to {output_path}")
    if output_path.endswith('.obj') and mtl_path:
        with open(output_path, 'w') as obj_file:
            # Write material library reference
            obj_file.write(f"mtllib {mtl_path}\n")

            # Write vertices
            for vertex in vertices:
                obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

            # Write vertex normals
            if mesh.has_vertex_normals():
                for normal in np.asarray(mesh.vertex_normals):
                    obj_file.write(f"vn {normal[0]} {normal[1]} {normal[2]}\n")

            # Write faces
            for face in faces:
                v_indices = [unique_vertex_indices[v] + 1 for v in face]  # OBJ indices start at 1
                obj_file.write(f"f {' '.join([f'{vi}//{vi}' for vi in v_indices])}\n")
    else:
        o3d.io.write_triangle_mesh(output_path, mesh, write_vertex_normals=True)

def visualize_mesh(mesh):
    # Visualize mesh
    print("Visualizing extracted mesh.")
    o3d.visualization.draw_geometries([mesh], window_name="Extracted Mesh of Selected Parts")

def main():
    args = parse_arguments()
    mesh = load_mesh(args.file)
    vertices, faces, unique_vertex_indices = extract_mesh(mesh)
    new_mesh = create_open3d_mesh(vertices, faces)
    save_mesh(new_mesh, args.output, vertices, faces, unique_vertex_indices, args.mtl)
    visualize_mesh(new_mesh)

if __name__ == "__main__":
    main()

import openmesh as om
import sys
import numpy as np
import argparse
import open3d as o3d

def parse_arguments():
    # Thêm argparse để xử lý tham số đầu vào
    parser = argparse.ArgumentParser(description="Extract, visualize, and save vertices of specific parts of the 3D mesh.")
    parser.add_argument("--file", type=str, required=True, help="Path to the 3D model file (.obj)")
    parser.add_argument("--output", type=str, required=True, help="Path to save the extracted point cloud (.ply)")
    return parser.parse_args()

def load_mesh(file_path):
    # Tải mô hình 3D bằng OpenMesh
    mesh = om.read_trimesh(file_path)
    # Kiểm tra nếu mesh đã được tải thành công
    if mesh.n_vertices() == 0:
        raise ValueError("Failed to load the mesh. Please check the file path and ensure the file is valid.")
    return mesh

def extract_vertices(mesh):
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

    vertices = []
    for part, vertex_indices in table_parts.items():
        part_vertices = mesh.points()[vertex_indices[0]:vertex_indices[1] + 1]
        vertices.append(part_vertices)

    vertices = np.vstack(vertices)
    return vertices

def create_open3d_point_cloud(vertices):
    # Chuyển đổi danh sách đỉnh thành Open3D PointCloud
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(vertices)
    return point_cloud

def save_point_cloud(point_cloud, output_path):
    # Lưu point cloud thành tệp .ply
    print(f"Saving point cloud to {output_path}")
    o3d.io.write_point_cloud(output_path, point_cloud)

def visualize_vertices(point_cloud):
    # Visualize vertices
    print("Visualizing extracted vertices.")
    o3d.visualization.draw_geometries([point_cloud], window_name="Extracted Vertices of Selected Parts")

def main():
    args = parse_arguments()
    mesh = load_mesh(args.file)
    vertices = extract_vertices(mesh)
    point_cloud = create_open3d_point_cloud(vertices)
    save_point_cloud(point_cloud, args.output)
    visualize_vertices(point_cloud)

if __name__ == "__main__":
    main()

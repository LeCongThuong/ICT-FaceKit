import openmesh as om
import sys
import numpy as np
import argparse
import open3d as o3d

def parse_arguments():
    # Thêm argparse để xử lý tham số đầu vào
    parser = argparse.ArgumentParser(description="Visualize a part of the 3D mesh with highlight.")
    parser.add_argument("--file", type=str, required=True, help="Path to the 3D model file (.obj)")
    parser.add_argument("--part", type=str, required=True, help="Name of the part to highlight")
    return parser.parse_args()

def load_mesh(file_path):
    # Tải mô hình 3D bằng OpenMesh
    mesh = om.read_trimesh(file_path)
    # Kiểm tra nếu mesh đã được tải thành công
    if mesh.n_vertices() == 0:
        raise ValueError("Failed to load the mesh. Please check the file path and ensure the file is valid.")
    return mesh

def get_highlighted_part(part_name):
    # Danh sách các bộ phận với vertex indices và polygon indices
    table_parts = {
        "Face": ([0, 9408], [0, 9229]),
        "Head and Neck": ([9409, 11247], [9230, 11143]),
        "Mouth socket": ([11248, 13293], [11144, 13225]),
        "Eye socket left": ([13294, 13677], [13226, 13629]),
        "Eye socket right": ([13678, 14061], [13630, 14033]),
        "Gums and tongue": ([14062, 17038], [14034, 17005]),
        "Teeth": ([17039, 21450], [17006, 21495]),
        "Eyeball left": ([21451, 23020], [21496, 23093]),
        "Eyeball right": ([23021, 24590], [23094, 24691]),
        "Lacrimal fluid left": ([24591, 24794], [24692, 24854]),
        "Lacrimal fluid right": ([24795, 24998], [24855, 25017]),
        "Eye blend left": ([24999, 25022], [25018, 25032]),
        "Eye blend right": ([25023, 25046], [25033, 25047]),
        "Eye occlusion left": ([25047, 25198], [25048, 25175]),
        "Eye occlusion right": ([25199, 25350], [25176, 25303]),
        "Eyelashes left": ([25351, 26034], [25304, 25843]),
        "Eyelashes right": ([26035, 26718], [25844, 26383])
    }
    # Kiểm tra xem phần cần highlight có tồn tại trong danh sách không
    if part_name not in table_parts:
        raise ValueError(f"Part '{part_name}' not found. Available parts: {', '.join(table_parts.keys())}")
    return table_parts[part_name]

def highlight_vertices(mesh, vertex_indices):
    # Hàm để thay đổi màu của các đỉnh của phần được chọn
    colors = np.full((mesh.n_vertices(), 3), [0.7, 0.7, 0.7])  # Màu xám nhạt cho toàn bộ mesh
    colors[vertex_indices[0]:vertex_indices[1] + 1] = [0, 0, 1]  # Màu xanh dương cho phần được highlight
    return colors

def convert_to_open3d_mesh(mesh, colors):
    # Chuyển đổi mesh thành Open3D TriangleMesh
    vertices = np.asarray(mesh.points())
    faces = np.asarray(mesh.face_vertex_indices())
    o3d_mesh = o3d.geometry.TriangleMesh()
    o3d_mesh.vertices = o3d.utility.Vector3dVector(vertices)
    o3d_mesh.triangles = o3d.utility.Vector3iVector(faces)
    o3d_mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
    return o3d_mesh

def visualize_mesh(o3d_mesh, part_name):
    # Visualize toàn bộ mesh với phần được highlight
    print(f"Visualizing head mesh with highlighted part: {part_name}")
    o3d.visualization.draw_geometries([o3d_mesh], window_name=f"Head with {part_name} highlighted")

def main():
    args = parse_arguments()
    mesh = load_mesh(args.file)
    highlighted_part = get_highlighted_part(args.part)
    colors = highlight_vertices(mesh, highlighted_part[0])
    o3d_mesh = convert_to_open3d_mesh(mesh, colors)
    visualize_mesh(o3d_mesh, args.part)

if __name__ == "__main__":
    main()

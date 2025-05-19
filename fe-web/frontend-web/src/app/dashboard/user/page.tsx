"use client";
import { useState, useEffect, use } from "react";
import { deleteUser } from "@/lib/api/user/delete_user";
import { getAllUsers } from "@/lib/api/user/get_users";
import { getUsersByRole } from "@/lib/api/user/get_user_by_role";
import { updateUserRole } from "@/lib/api/user/put_user";
import style from "@/app/dashboard/user/user.module.scss"
import tableStyle from "@/styles/table.module.scss"
interface userResponse {
    id: string;
    username: string;
    email: string;
    role: string;
    created_at: Date;

}

const dashboardUser = () => {
    const [users, setUsers] = useState<userResponse[]>([])
    const [roles, setRoles] = useState<string>("all")
    const roleOptions: string[] = ["admin", "supervisor", "viewer"];
    // Lấy tất cả người
    const TakeAllUsers = async () => {
        try {
            const data = await getAllUsers();
            setUsers(data);
        } catch (error) {
            console.error(error);
        }
    }
    // Lấy nguồi dùng theo role
    const TakeUserByRole = async (role: string) => {
        try {
            const data = await getUsersByRole(role);
            setUsers(data);
        } catch (error) {
            console.error(error);
        }
    }
    // Lấy người dùng dựa theo bộ lọc role
    const TakeUserData = async () => {
        try {
            if (roles === "all") {
                await TakeAllUsers();
            } else {
                await TakeUserByRole(roles);
            }
        } catch (error) {
            console.error(error);
        }
    }
    useEffect(() => {
        TakeUserData();
    }, [roles])
    // Hàm cấp quyền cho user
    const grand_permission = async (username: string, role: string) => {
        try {
            const newUser = await updateUserRole(username, role);
            setUsers(users.map((u) => u.username == username ? newUser : u));
            TakeUserData();
        } catch (error) {
            console.error(`Error: ${error}`);
        }

    }
    // Hàm xóa người dùng
    const delete_user = async (username: string) => {
        const confirmDelete = window.confirm('Bạn có chắc muốn xóa người dung này không?')
        if (confirmDelete) {
            try {
                const response = await deleteUser(username);
                if (response.detail) {
                    alert(response.detail);
                } else {
                    setUsers(users.filter((user) => user.username !== username));
                    alert(response.message);
                }
            } catch (error) {
                console.error(error);
            }
        }

    }
    return (
        <div className={style.container}>
            <h1 className={style.title}>Danh sách người dùng</h1>
            <div className={style.selectUser}>
                <label>Lọc người dùng theo quyền: </label>
                <select
                    value={roles}
                    onChange={(e) => setRoles(e.target.value)}
                >
                    <option value="all">Tất cả người dùng</option>
                    {roleOptions.map((role, index) => (
                        <option key={index} value={role}>
                            {role}
                        </option>
                    ))}
                </select>
            </div>
            <div className={style.tableContainer}>
                <table className={tableStyle.table}>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tên người dùng</th>
                            <th>Quyền</th>
                            <th>Email</th>
                            <th>Thời gian tạo</th>
                            <th>Thao tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((user, index) => (
                            <tr key={index}>
                                <td>{user.id}</td>
                                <td>{user.username}</td>
                                <td>{user.role}</td>
                                <td>{user.email}</td>
                                <td>{user.created_at.toLocaleString()}</td>
                                <td><div className={style.list_button}>
                                    <button
                                        onClick={() => {
                                            (user.role === "supervisor" || user.role === "admin")
                                                ? null
                                                : grand_permission(user.username, "supervisor");
                                        }}
                                        disabled={user.role === "supervisor" || user.role === "admin"}
                                    >
                                        Cấp quyền
                                    </button>
                                    <button
                                        onClick={() => {
                                            (user.role === "supervisor")
                                                ? grand_permission(user.username, "viewer")
                                                : null;
                                        }}
                                        disabled={user.role === "viewer" || user.role === "admin"}
                                    >
                                        Bỏ quyền
                                    </button>
                                    <button onClick={() => { delete_user(user.username) }} disabled={user.role === "admin"}>❌</button>
                                </div></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
export default dashboardUser
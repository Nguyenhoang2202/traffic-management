'use client';
import { useState } from 'react';
import { useEffect } from 'react';
import { getAllCommands } from '@/lib/api/manager/get_commands'
import { getCommandsByUser } from '@/lib/api/manager/get_command'
import { getAllUsers } from '@/lib/api/user/get_users'
import style from '@/app/dashboard/command/command.module.scss'
import tableStyle from '@/styles/table.module.scss'
interface commandFormatData {
    username: string;
    user_id: string;
    device_id: string;
    mode?: number | null;
    auto_mode?: boolean | null;
    green_time?: number | null;
    red_time?: number | null;
    timestamp?: Date | null;
}

interface userFormatData {
    id: string;
    username: string;
}

const CommandManager = () => {
    const [commandData, setCommandData] = useState<commandFormatData[]>([]);
    const [userID, setUserID] = useState<string>('all');
    const [users, setUsers] = useState<userFormatData[]>([]);

    // Lấy danh sách user
    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const data = await getAllUsers();
                setUsers(data);
            } catch (error) {
                console.error('Error getting users:', error);
            }
        };
        fetchUsers();
    }, []);

    // Lấy danh sách command theo userID (hoặc tất cả)
    useEffect(() => {
        const callData = async () => {
            try {
                let data;
                if (userID === 'all') {
                    data = await getAllCommands();
                } else {
                    data = await getCommandsByUser(userID);
                }
                setCommandData(data);
            } catch (error) {
                console.error('Error getting commands:', error);
            }
        };
        callData();
    }, [userID]);

    return (
        <div className={style.container}>
            <h1 className={style.title}>Danh sách điều chỉnh</h1>
            <div className={style.selectUser}>
                <label>Chọn người dùng: </label>
                <select
                    value={userID}
                    onChange={(e) => setUserID(e.target.value)}
                >
                    <option value="all">Tất cả người dùng</option>
                    {users.map((user) => (
                        <option key={user.id} value={user.id}>
                            {user.username}
                        </option>
                    ))}
                </select>
            </div>
            <div className={style.tableContainer}>
                <table className={tableStyle.table}>
                    <thead>
                        <tr>
                            <th>Người gửi</th>
                            <th>Camera</th>
                            <th>Chế độ (mode)</th>
                            <th>Tự động</th>
                            <th>Thời gian đèn xanh (giây)</th>
                            <th>Thời gian đèn đỏ (giây)</th>
                            <th>Thời gian gửi</th>
                        </tr>
                    </thead>
                    <tbody>
                        {commandData.map((command, index) => (
                            <tr key={index}>
                                <td>{command.username}</td>
                                <td>{command.device_id}</td>
                                <td>{command.mode === 0 ? 'Bình thường' : command.mode === 1 ? 'Nhấp nháy' : ''}</td>
                                <td>{command.auto_mode ? 'Tự động' : 'Thủ công'}</td>
                                <td>{command.green_time}</td>
                                <td>{command.red_time}</td>
                                <td>{command.timestamp ? new Date(command.timestamp).toLocaleString() : ''}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
export default CommandManager
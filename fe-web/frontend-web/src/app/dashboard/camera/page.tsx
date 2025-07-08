'use client';

import { useEffect, useState, useRef } from 'react';
import { getCameras } from '@/lib/api/camera/get_cameras';
import StatusMap from '@/components/common/Map';
import { WebSocketClient } from "@/lib/api/websocket/wsClient";
import style from "@/app/dashboard/camera/camera.module.scss"
import tableStyle from '@/styles/table.module.scss'

interface RawCameraData {
    device_id: string;
    latitude: number;
    longitude: number;
}

interface CameraWithStatus {
    device_id: string;
    lat: number;
    lng: number;
    label: string;
    status: 'active' | 'warning' | 'offline';
}
interface DeviceData {
    light_state: number;
    remaining_time: number;
    device_id: string;
    img_detected: string;
    num_current: number;
    num_total: number;
    cover_ratio: number;
    mode: number;
    auto_mode: number;
}
const MapCamera = () => {
    const [cameras, setCameras] = useState<CameraWithStatus[]>([]);
    const [mapCenter, setMapCenter] = useState<{ lat: number; lng: number } | null>(null);
    const [viewPos, setViewPos] = useState<{ lat: number; lng: number } | null>(null);
    const [getClick, setGetClick] = useState<boolean>(false);
    const [devices, setDevices] = useState<DeviceData[]>([]);
    // Fake data
    const statusIndexRef = useRef(0);
    const statusCycle: CameraWithStatus['status'][] = ['active', 'warning', 'offline'];
    // --
    useEffect(() => {
        const wsClient = new WebSocketClient((data) => {
            setDevices(data);
        }, 1, 10);

        return () => {
            wsClient.closeManually();
        };
    }, []);

    // useEffect(() => {
    //     const fetchCamera = async () => {
    //         try {
    //             const rawData: RawCameraData[] = await getCameras();

    //             const processedData: CameraWithStatus[] = rawData.map((cam, index) => ({
    //                 device_id: cam.device_id,
    //                 lat: cam.latitude,
    //                 lng: cam.longitude,
    //                 label: `Camera ${cam.device_id}: offline`, // hoặc `Camera ${cam.device_id}`
    //                 status: 'offline', // bạn có thể thay đổi logic ở đây
    //             }));

    //             setCameras(processedData);

    //             // Set center map từ camera đầu tiên
    //             if (processedData.length > 0) {
    //                 setMapCenter({ lat: processedData[0].lat, lng: processedData[0].lng });
    //             }
    //         } catch (error) {
    //             console.error('Error getting cameras:', error);
    //         }
    //     };

    //     fetchCamera();
    // }, []);
    // Fake data
    useEffect(() => {
        const fetchCamera = async () => {
            try {
                const rawData: RawCameraData[] = await getCameras();

                const statusCycle: CameraWithStatus['status'][] = ['active', 'warning', 'offline'];

                const processedData: CameraWithStatus[] = rawData.map((cam, index) => {
                    const status = statusCycle[index % statusCycle.length];
                    return {
                        device_id: cam.device_id,
                        lat: cam.latitude,
                        lng: cam.longitude,
                        label: `Camera ${cam.device_id}: ${status}`,
                        status,
                    };
                });

                setCameras(processedData);

                if (processedData.length > 0) {
                    setMapCenter({ lat: processedData[0].lat, lng: processedData[0].lng });
                }
            } catch (error) {
                console.error('Error getting cameras:', error);
            }
        };

        fetchCamera();
    }, []);

    // --


    useEffect(() => {
        if (devices.length === 0 || cameras.length === 0) return;
        console.log(`cameras: ${cameras},devices:${devices}`)
        const updatedCameras = cameras.map((cam) => {
            const matchingDevice = devices.find((d) => d.device_id === cam.device_id);
            if (!matchingDevice) {
                return {
                    ...cam,
                    status: 'offline' as 'offline',
                    label: `Camera ${cam.device_id}: offline`,
                };
            }
            return {
                ...cam,
                status: (matchingDevice.cover_ratio > 0.5 ? 'warning' : 'active') as 'active' | 'warning',
                label: `Camera ${cam.device_id}: ${matchingDevice.cover_ratio > 0.5 ? 'warning' : 'active'}`,
            };
        });

        setCameras(updatedCameras);
    }, [devices]);

    const changeCameraLocation = (device_id: string) => {
        const camera = cameras.find(cam => cam.device_id === device_id);
        if (camera) {
            setViewPos({ lat: camera.lat, lng: camera.lng });
            setGetClick(true)
            console.log(`Chang here:${camera.lat},${camera.lng}`)
        }
    }
    return (
        <div className={style.container}>
            <h1 className={style.title}>Bản đồ camera</h1>
            <div className={style.wrap_map}>
                {mapCenter && (
                    <StatusMap
                        getClick={getClick}
                        onViewDone={() => setGetClick(false)}
                        points={cameras}
                        center={[mapCenter.lat, mapCenter.lng]}
                        viewPosition={viewPos ? [viewPos.lat, viewPos.lng] : undefined}
                    />
                )}
            </div>
            <div className={style.tableContainer}>
                <table className={tableStyle.table}>
                    <thead>
                        <tr>
                            <th>Camera</th>
                            <th>Vĩ độ</th>
                            <th>Kinh độ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cameras.map((camera, index) => (
                            <tr key={index} onClick={() => changeCameraLocation(camera.device_id)}>
                                <td>{camera.device_id}</td>
                                <td>{camera.lat}</td>
                                <td>{camera.lng}</td></tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default MapCamera;

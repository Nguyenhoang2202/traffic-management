import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect } from 'react';
import dynamic from 'next/dynamic';

const PulseMarker = dynamic(() => import('./PulseMarker').then(mod => mod.PulseMarker), {
    ssr: false,
});

export interface StatusPoint {
    lat: number;
    lng: number;
    status: 'active' | 'warning' | 'offline';
    label?: string;
}

interface StatusMapProps {
    points: StatusPoint[];
    center?: [number, number];
    zoom?: number;
    viewPosition?: [number, number];
    getClick: boolean;
    onViewDone?: () => void;  // <-- Callback để reset từ component cha
}

const statusColorMap: Record<StatusPoint['status'], string> = {
    active: 'green',
    warning: 'red',
    offline: 'grey',
};

function RecenterMap({
    position,
    getClick,
    onViewDone,
}: {
    position: [number, number];
    getClick: boolean;
    onViewDone?: () => void;
}) {
    const map = useMap();

    useEffect(() => {
        if (getClick) {
            map.setView(position, map.getZoom(), { animate: true });
            console.log("FIXX");
            if (onViewDone) {
                onViewDone();  // Gọi về cha để reset getClick
            }
        }
    }, [getClick, position, map, onViewDone]);

    return null;
}

export default function StatusMap({
    points,
    center = [10.762622, 106.660172],
    viewPosition = [0, 0],
    zoom = 13,
    getClick = false,
    onViewDone,  // <-- truyền xuống
}: StatusMapProps) {
    return (
        <div style={{ height: '100%', width: '100%' }}>
            <MapContainer
                center={center as [number, number]}
                zoom={zoom}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    attribution='&copy; OpenStreetMap contributors'
                    url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
                />

                {viewPosition && (
                    <RecenterMap
                        position={viewPosition}
                        getClick={getClick}
                        onViewDone={onViewDone}
                    />
                )}

                {points.map((point, index) => {
                    const color = statusColorMap[point.status];

                    if (point.status === 'warning') {
                        return (
                            <PulseMarker
                                key={index}
                                lat={point.lat}
                                lng={point.lng}
                                color={statusColorMap[point.status]}
                            />
                        );
                    }

                    return (
                        <CircleMarker
                            key={index}
                            center={[point.lat, point.lng]}
                            radius={8}
                            pathOptions={{
                                color,
                                fillColor: color,
                                fillOpacity: 0.9,
                            }}
                        >
                            {point.label && <Tooltip>{point.label}</Tooltip>}
                        </CircleMarker>
                    );
                })}
            </MapContainer>
        </div>
    );
}

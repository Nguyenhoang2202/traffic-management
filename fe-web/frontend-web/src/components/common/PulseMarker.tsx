'use client'

import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { useEffect } from 'react';

export interface PulseMarkerProps {
    lat: number;
    lng: number;
    color?: string;
}

export const PulseMarker = ({ lat, lng, color = 'green' }: PulseMarkerProps) => {
    const map = useMap();

    useEffect(() => {
        const icon = L.divIcon({
            className: '',
            html: `
        <div class="pulse-marker">
            <div class="pulse-circle" style="background-color: ${color}80;"></div>
            <div class="pulse-core" style="background-color: ${color};"></div>
        </div>
      `,
            iconSize: [40, 40],
            iconAnchor: [10, 10], // trung tâm của icon
        });

        const marker = L.marker([lat, lng], { icon }).addTo(map);

        return () => {
            map.removeLayer(marker);
        };
    }, [lat, lng, map, color]);

    return null;
};

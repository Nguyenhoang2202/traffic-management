import {
    ResponsiveContainer,
    LineChart,
    BarChart,
    PieChart,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    Pie,
    Cell,
} from "recharts";

type ChartType = "line" | "bar" | "pie";

interface ChartRendererProps {
    type: ChartType;
    data: any[];
    dataKeyX?: string;
    dataKeyY?: string | string[];
    dataKeyLabels?: Record<string, string>; // 👈 thêm để đổi tên các key
    dataKeyPieName?: string;
    dataKeyPieValue?: string;
    colors?: string[];
    height?: number;
}

const ChartRenderer = ({
    type,
    data,
    dataKeyX = "name",
    dataKeyY = "value",
    dataKeyLabels = {}, // 👈 mặc định rỗng
    dataKeyPieName = "name",
    dataKeyPieValue = "value",
    colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300"],
    height = 300,
}: ChartRendererProps) => {
    let chart;
    const keys = Array.isArray(dataKeyY) ? dataKeyY : [dataKeyY];
    switch (type) {
        case "line":
            const lineKeys = keys;
            chart = (
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey={dataKeyX}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                    />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {lineKeys.map((key, index) => (
                        <Line
                            key={key}
                            type="monotone"
                            dataKey={key}
                            name={dataKeyLabels[key] || key} // 👈 dùng tên custom nếu có
                            stroke={colors[index % colors.length]}
                            strokeWidth={3}
                            dot={false}
                        />
                    ))}
                </LineChart>
            );
            break;

        case "bar":
            const barKeys = keys;
            chart = (
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey={dataKeyX} angle={-45} textAnchor="end" height={60} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {barKeys.map((key, index) => (
                        <Bar
                            key={key}
                            dataKey={key}
                            name={dataKeyLabels[key] || key} // 👈 tên custom
                            fill={colors[index % colors.length]}
                        />
                    ))}
                </BarChart>
            );
            break;

        case "pie":
            chart = (
                <PieChart>
                    <Tooltip />
                    <Legend />
                    <Pie
                        data={data}
                        dataKey={dataKeyPieValue}
                        nameKey={dataKeyPieName}
                        outerRadius={80}
                        fill={colors[2]}
                        label
                    >
                        {data.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                        ))}
                    </Pie>
                </PieChart>
            );
            break;
    }

    return (
        <ResponsiveContainer width="100%" height={height}>
            {chart}
        </ResponsiveContainer>
    );
};

export default ChartRenderer;

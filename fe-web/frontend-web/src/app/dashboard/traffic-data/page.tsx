'use client'
import { useEffect, useState } from "react";
import style from '@/app/dashboard/traffic-data/traffic_data.module.scss'
import { getDatas } from '@/lib/api/traffic-data/get_traffic_datas'
import { getData } from '@/lib/api/traffic-data/get_traffic_data'
import { getPredictDatas } from '@/lib/api/predict-data/get_predict_datas'
import { getPredictData } from '@/lib/api/predict-data/get_predict_data'
import { downloadExcelData } from '@/lib/api/traffic-data/get_excel_traffic_data'
import { downloadExcelDatas } from '@/lib/api/traffic-data/get_excel_traffic_datas'
import ChartRenderer from "@/components/common/Chart";
import ParameterBoardRender from "@/components/common/Parameter_board";


const TrafficData = () => {
    const [trafficData, setTrafficData] = useState<any[]>([])
    const [predictData, setPredictData] = useState<any[]>([])
    // Khởi tạo dữ liệu
    useEffect(() => {
        const getAllData = async () => {
            try {
                const rawData = await getData("C1");
                const rawPredictData = await getPredictData("C1");
                const processed = rawData.map((d: any) => ({
                    ...d,
                    timestamp: new Date(d.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                    }),
                }));
                setTrafficData(processed);
                const PredictProcessed = rawPredictData.map((d: any) => ({
                    ...d,
                    predict_for_time: new Date(d.predict_for_time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                    }),
                }));
                setPredictData(PredictProcessed);
            } catch (error) {
                console.error('Error traffic_data get all:', error);
            }
        };
        getAllData();
    }, []);

    return (
        <div className={style.container}>
            <h1 className={style.title}>Dữ liệu giao thông</h1>
            <button className={style.btn_down_all}
                onClick={() => { downloadExcelDatas(); }}
            >
                Download all data
            </button>
            <div className={style.chart_board}>
                <h2 className={style.board_title}>
                    Bảng dữ liệu camera: C1 <br />
                    <button
                        className={style.btn_down_one_camera}
                        onClick={() => { downloadExcelData("C1"); }}
                    >
                        Download data
                    </button>
                </h2>


                <div className={style.total_chart}>
                    <ChartRenderer
                        type="line"
                        data={trafficData}
                        dataKeyX="timestamp"
                        dataKeyY={["num_total", "average_green_time"]}
                        dataKeyLabels={{
                            num_total: "Tổng lưu lượng xe",
                            average_green_time: "Thời gian đèn xanh trung bình"
                        }}
                    />
                </div>
                <div className={style.predict_chart}>
                    <ChartRenderer
                        type="line"
                        data={predictData}
                        dataKeyX="predict_for_time"
                        dataKeyY={"prediction"}
                        colors={["#FFD405"]}
                        dataKeyLabels={{
                            prediction: "Tổng lưu lượng xe dự đoán"
                        }}
                    />
                </div>
                <div className={style.rain_chart}>
                    <ChartRenderer
                        type="bar"
                        data={trafficData}
                        dataKeyX="timestamp"
                        dataKeyY="rain"
                        dataKeyLabels={{
                            rain: "Mưa"
                        }}
                    />
                </div>
                <div className={style.list_parameter_board}>
                    <h2>Dữ liệu mới nhất</h2>
                    <div className={style.parameter_item}>
                        <ParameterBoardRender label="Tổng thời gian đèn xanh" data={trafficData.length > 0 ? trafficData[trafficData.length - 1].all_green_time : 0} />
                    </div>
                    <div className={style.parameter_item}>
                        <ParameterBoardRender label="Tổng số lần đèn chuyển xanh" data={trafficData.length > 0 ? trafficData[trafficData.length - 1].numb_turn_green : 0} />
                    </div>
                    <div className={style.parameter_item}>
                        <ParameterBoardRender label="Mưa" data={trafficData.length > 0 ? trafficData[trafficData.length - 1].rain : 0} />
                    </div>
                </div>
            </div>
        </div>
    );
}
export default TrafficData
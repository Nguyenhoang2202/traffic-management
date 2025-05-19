import style from '@/styles/common/parameter.module.scss';

interface ParameterBoardProps {
    label: string;
    data: number;
}

const ParameterBoardRender = ({ label, data }: ParameterBoardProps) => {
    return (
        <div className={style.parameter_item}>
            <h2 className={style.label}>{label}</h2>
            <p className={style.value}>{data}</p>
        </div>
    );
};

export default ParameterBoardRender;

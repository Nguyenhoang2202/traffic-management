export type FieldType = "text" | "email" | "password" | "textarea" | "select" | "checkbox" | "number";

interface Field {
    name: string;
    label: string;
    type: FieldType;
    option?: string[];
    min?: number;
    max?: number;
    step?: number;
}

interface FormProps {
    nameForm: string;
    fields: Field[];
    onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
    onChange: (e: React.ChangeEvent<any>) => void;
    values: Record<string, any>;
}

const Form: React.FC<FormProps> = ({ nameForm, fields, onSubmit, onChange, values }) => {
    return (
        <form onSubmit={onSubmit} className="space-y-4">
            <h1 className="text-xl font-bold">{nameForm}</h1>

            {fields.map((field, index) => (
                <div key={index} className="flex flex-col">
                    <label htmlFor={field.name} className="mb-1">{field.label}</label>

                    {field.type === "textarea" ? (
                        <textarea
                            name={field.name}
                            id={field.name}
                            value={values[field.name] || ""}
                            onChange={onChange}
                            rows={4}
                            className="border rounded p-2"
                        />
                    ) : field.type === "select" ? (
                        <select
                            name={field.name}
                            id={field.name}
                            value={values[field.name] || ""}
                            onChange={onChange}
                            className="border rounded p-2"
                        >
                            <option value="">-- Chọn --</option>
                            {field.option?.map((opt, i) => (
                                <option key={i} value={opt}>{opt}</option>
                            ))}
                        </select>
                    ) : field.type === "checkbox" ? (
                        <input
                            type="checkbox"
                            name={field.name}
                            id={field.name}
                            checked={values[field.name] || false}
                            onChange={onChange}
                        />
                    ) : field.type === "number" ? (
                        <input
                            type="number"
                            name={field.name}
                            id={field.name}
                            value={values[field.name] || ""}
                            onChange={onChange}
                            className="border rounded p-2"
                            min={field.min}
                            max={field.max}
                            step={field.step}
                        />
                    ) : (
                        <input
                            type={field.type}
                            name={field.name}
                            id={field.name}
                            value={values[field.name] || ""}
                            onChange={onChange}
                            className="border rounded p-2"
                        />
                    )}
                </div>
            ))}

            <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">
                {nameForm}
            </button>
        </form>
    );
};

export default Form;

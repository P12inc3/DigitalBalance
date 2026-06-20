interface InputFieldProps {
  label: string;
  type: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  autoComplete?: string;
}

export function InputField({
  label,
  type,
  value,
  onChange,
  placeholder,
  autoComplete,
}: InputFieldProps) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm text-ink-muted">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        className="w-full rounded-lg border border-base-600 bg-base-800 px-4 py-2.5 text-ink placeholder:text-ink-faint focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
      />
    </label>
  );
}

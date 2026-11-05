import frappeUIPreset, { content } from 'frappe-ui/tailwind'

export default {
  presets: [frappeUIPreset],
  content: [
    ...content,
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

export const defaultLayoutConfig = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: {
    family: 'system-ui, -apple-system, sans-serif',
    color: '#4b5563',
  },
  margin: { t: 40, b: 40, l: 40, r: 40 },
  showlegend: true,
  hovermode: 'closest' as const,
};

export const plotConfig = {
  responsive: true,
  displayModeBar: false,
};
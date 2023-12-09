const {
  SciChartSurface,
  SciChart3DSurface,
  NumericAxis,
  EAutoRange,
  XyDataSeries,
  FastLineRenderableSeries,
  CameraController,
  MouseWheelZoomModifier3D,
  OrbitModifier3D,
  ResetCamera3DModifier,
  NumericAxis3D,
} = SciChart;

SciChartSurface.UseCommunityLicense();

async function createSimpleDynamicChart(elementId, color) {
  const { wasmContext, sciChartSurface } = await SciChartSurface.createSingle(
    elementId
  );

  const xAxis = new NumericAxis(wasmContext, { autoRange: EAutoRange.Always });
  const yAxis = new NumericAxis(wasmContext, { autoRange: EAutoRange.Always });
  sciChartSurface.xAxes.add(xAxis);
  sciChartSurface.yAxes.add(yAxis);

  const dataSeries = new XyDataSeries(wasmContext, {
    containsNaN: false,
    isSorted: true,
  });

  sciChartSurface.renderableSeries.add(
    new FastLineRenderableSeries(wasmContext, {
      dataSeries,
      strokeThickness: 2,
      stroke: color,
    })
  );

  return (x, y) => {
    dataSeries.append(x, y);
  };
}

(async () => {
  const dataEntries = [
    await createSimpleDynamicChart('temperature', '#eba134'),
    await createSimpleDynamicChart('pressure', '#34eb83'),
    await createSimpleDynamicChart('humidity', '#3489eb'),
    await createSimpleDynamicChart('ambient-light', '#eb34c7'),
    await createSimpleDynamicChart('battery', '#ffffff'),
  ];

  const socket = new WebSocket('ws://localhost');

  socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    console.log(data);

    switch (data.type) {
      case 'sensors-data': {
        const { temperature, pressure, humidity, ambientLight, batteryLevel } =
          data.data;
        dataEntries[0](data.time, temperature);
        dataEntries[1](data.time, pressure);
        dataEntries[2](data.time, humidity);
        dataEntries[3](data.time, ambientLight);
        dataEntries[4](data.time, batteryLevel);

        document.getElementById(
          'battery-text'
        ).innerText = `Battery: ${batteryLevel}%`;
      }

      default:
        break;
    }
  });
})();

/**
 * ECharts tree-shaking entry (pilot, reversible).
 *
 * Imports only what the pilot uses: BarChart + HeatmapChart, Grid +
 * Tooltip + Legend + VisualMap components, SVGRenderer. Nothing else from
 * `echarts` enters the `echarts` chunk.
 */
import * as echarts from 'echarts/core';
import { BarChart, HeatmapChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
} from 'echarts/components';
import { SVGRenderer } from 'echarts/renderers';
import { registerLandAgriThemes } from '../../../lib/echarts-theme';

echarts.use([
  BarChart,
  HeatmapChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
  SVGRenderer,
]);

registerLandAgriThemes(echarts);

export { echarts };
export default echarts;

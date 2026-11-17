import {
  Canvas, defineComponent, defineComposition, field, useInstance, useTime,
  basicTransformParameters, basicTransformMatrix,
} from '@motionharness/sdk';

// Use as a Pro entry, with mh.json.entry pointing to this file. Edit the Title row.
// A single Canvas keeps the drawing together; it has no per-object drag handles.
const Title = defineComponent({
  id: 'selected-title',
  parameters: {
    text: field.text({label: '文字', default: 'MotionHarness'}),
    color: field.color({label: '颜色', default: '#f4f6f8', animatable: true}),
    ...basicTransformParameters({
      defaults: {x: 64, y: 140},
      animations: {opacity: {keyframes: [{time: 0, value: 0}, {time: 0.4, value: 1}]}},
    }),
  },
  component: () => null, // This instance supplies values; the shared Canvas draws it.
});

function drawBackground(context: CanvasRenderingContext2D, time: number) {
  context.fillStyle = '#14212b';
  context.fillRect(0, 0, 640, 360);
  context.fillStyle = '#e68a45';
  context.beginPath();
  context.arc(96 + 48 * Math.sin(time * 2), 64, 16, 0, Math.PI * 2);
  context.fill();
}

const Scene = defineComponent({
  id: 'selected-editing',
  parameters: {title: field.component({label: '标题', component: Title})},
  component({title}) {
    const time = useTime(), selected = useInstance(title);
    return <Canvas width={640} height={360} draw={({context}) => {
      drawBackground(context, time); // Background keeps project time when Title is retimed.
      if (!selected.visible) return;
      const values = selected.values;
      context.save();
      context.translate(values.x, values.y);
      const matrix = basicTransformMatrix(values);
      context.transform(matrix.a, matrix.b, matrix.c, matrix.d, 0, 0);
      context.globalAlpha = values.opacity;
      context.fillStyle = values.color;
      context.font = 'bold 40px sans-serif';
      context.textBaseline = 'top';
      context.fillText(values.text, -values.anchorX, -values.anchorY);
      context.restore();
    }}/>;
  },
});

export default defineComposition({id: 'selected-editing', component: Scene,
  width: 640, height: 360, duration: 3, fps: 30});

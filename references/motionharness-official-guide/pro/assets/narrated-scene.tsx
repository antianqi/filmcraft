import {
  defineComponent, defineComposition, field, Instance, Layer,
  basicTransformParameters, basicTransformValue, basicSizeParameters,
} from '@motionharness/sdk';

// Copy to src/NarratedScene.tsx and call this from the project entry.
// Supply duration/cueTime from the original and Agent/user timing, not a guessed beat.
// Add the supplied audio to the root with `mh audio edit` during initial creation.
export function createNarratedScene({id = 'narrated-scene', duration = 3, cueTime = 1.4} = {}) {
  const Text = defineComponent({
    id: 'narration-text',
    parameters: {
      text: field.text({label: '文字', default: '把想法'}),
      color: field.color({label: '颜色', default: '#edf4e9', animatable: true}),
      fontSize: field.number({label: '字号', default: 64, min: 1, animatable: true}),
      ...basicTransformParameters(),
      ...basicSizeParameters(800, 80),
    },
    component(values) {
      return <Layer bindings="parameters" value={basicTransformValue(values)} style={{position: 'absolute', left: 0, top: 0}}>
        <div style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: values.color, fontSize: values.fontSize, whiteSpace: 'pre-wrap'}}>{values.text}</div>
      </Layer>;
    },
  });
  const Progress = defineComponent({
    id: 'narration-progress',
    parameters: {
      progress: field.number({label: '进度', default: 0, min: 0, max: 1, animatable: true, defaultAnimation: {keyframes: [{time: 0, value: 0}, {time: duration, value: 1}]}}),
      color: field.color({label: '进度颜色', default: '#bfe98b', animatable: true}),
      background: field.color({label: '轨道颜色', default: '#304348'}),
      ...basicTransformParameters({defaults: {x: 150, y: 280}}),
      ...basicSizeParameters(500, 8),
    },
    component(values) {
      return <Layer bindings="parameters" value={basicTransformValue(values)} style={{position: 'absolute', left: 0, top: 0}}>
        <div style={{width: '100%', height: '100%', borderRadius: 4, background: values.background, overflow: 'hidden'}}>
          <div style={{width: `${values.progress * 100}%`, height: '100%', background: values.color}}/>
        </div>
      </Layer>;
    },
  });
  const Readout = defineComponent({
    id: 'narration-readout',
    parameters: {
      prefix: field.text({label: '前缀', default: '内容时间 '}),
      seconds: field.number({label: '显示秒数', default: 0, animatable: true, defaultAnimation: {keyframes: [{time: 0, value: 0}, {time: duration, value: duration}]}}),
      suffix: field.text({label: '后缀', default: ' s'}),
      color: field.color({label: '颜色', default: '#edf4e9', animatable: true}),
      fontSize: field.number({label: '字号', default: 24, min: 1, animatable: true}),
      ...basicTransformParameters({defaults: {y: 310}}),
      ...basicSizeParameters(800, 36),
    },
    component(values) {
      return <Layer bindings="parameters" value={basicTransformValue(values)} style={{position: 'absolute', left: 0, top: 0}}>
        <div style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: values.color, fontSize: values.fontSize}}>{values.prefix}{values.seconds.toFixed(3)}{values.suffix}</div>
      </Layer>;
    },
  });
  const Visuals = defineComponent({
    id: 'narration-visuals',
    parameters: {
      ...basicTransformParameters(),
      ...basicSizeParameters(800, 450),
      heading: field.component({label: '标题', component: Text, initialProps: {text: '声音与画面 · 共享时间', fontSize: 22, y: 106, height: 34}}),
      first: field.component({label: '前半句', component: Text, timing: {start: 0, duration: cueTime}, initialProps: {text: '把想法', y: 166}}),
      second: field.component({label: '后半句', component: Text, timing: {start: cueTime, duration: duration - cueTime}, initialProps: {text: '变成画面', color: '#bfe98b', y: 166}}),
      progress: field.component({label: '进度条', component: Progress}),
      readout: field.component({label: '时间读数', component: Readout}),
    },
    component(values) {
      return <Layer bindings="parameters" value={basicTransformValue(values)} style={{position: 'absolute', left: 0, top: 0}}>
        <Instance value={values.heading}/><Instance value={values.first}/><Instance value={values.second}/>
        <Instance value={values.progress}/><Instance value={values.readout}/>
      </Layer>;
    },
  });
  const Scene = defineComponent({
    id: 'scene',
    parameters: {
      background: field.color({label: '画布背景', default: '#132024'}),
      visuals: field.component({label: '画面', component: Visuals, timing: {start: 0, duration}}),
    },
    component: ({background, visuals}) => <div style={{position: 'relative', width: '100%', height: '100%', background, fontFamily: 'sans-serif'}}><Instance value={visuals}/></div>,
  });
  return defineComposition({id, component: Scene, width: 800, height: 450, fps: 30, duration});
}

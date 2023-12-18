
const ixFirstData = 50;
const ixLastData = 90;

const readers = {};

var g_renderer;
var g_renderWindow;
var g_mapper;
var g_actor;

function initialise() {

  const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
  const renderer = vtk.Rendering.Core.vtkRenderer.newInstance({ background: [0.2, 0.3, 0.4] });
  renderWindow.addRenderer(renderer);

  const openglRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
  renderWindow.addView(openglRenderWindow);

  const container = document.getElementById('vtkcanvas');
  openglRenderWindow.setContainer(container);
  const { width, height } = container.getBoundingClientRect();
  openglRenderWindow.setSize(width, height);

  const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
  interactor.setView(openglRenderWindow);
  interactor.initialize();
  interactor.bindEvents(container);
  isty = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
  interactor.setInteractorStyle(isty);

  g_renderer = renderer;
  g_renderWindow = renderWindow;

  function loadXMLData(dataIx = ixFirstData, maxIx = ixLastData) {
    const reader = vtk.IO.XML.vtkXMLPolyDataReader.newInstance();

    const loadText = document.getElementById("fileNumber");
    while( loadText.firstChild ) {
      loadText.removeChild( loadText.firstChild );
    }
    loadText.appendChild(document.createTextNode(`${dataIx - ixFirstData + 1} of ${ixLastData - ixFirstData + 1}`));

    reader.setUrl(`data/limb/limb_rec_2${dataIx}.vtp`).then(() => {
      readers[dataIx] = reader;

      if (dataIx < maxIx) {
        // Chain promise...
        // Continue loading data files in sequence until there are none remaining
        loadXMLData(dataIx + 1, maxIx);
      } else {
        const reader = readers[ixFirstData];

        drawWithReader(reader, dataIx);

        const loadingIndicator = document.getElementById("loadingIndicator");
        loadingIndicator.style.display = "none";

        setTimeStageString(ixFirstData);

        const tsSlider = document.getElementById("timeStageSlider");
        tsSlider.min = ixFirstData;
        tsSlider.max = ixLastData;
        tsSlider.value = ixFirstData;
      }
    });
  }

  loadXMLData();
}

function drawWithReader(reader, i) {
  const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
  const actor = vtk.Rendering.Core.vtkActor.newInstance();

  g_renderer.removeActor(g_actor);

  g_mapper = mapper;
  g_actor = actor;

  mapper.setInputConnection(reader.getOutputPort());
  actor.setMapper(mapper);
  // actor.getProperty().setColor(1.0, 1.0, 0.0)

  g_renderer.addActor(actor);

  // g_renderer.resetCamera();
  const camera = g_renderer.getActiveCamera();
  // console.log(i)
  // console.log(camera.getPosition());
  // console.log(camera.getFocalPoint());
  // console.log(camera.getViewUp());
  // console.log(camera.getClippingRange());
  if (i==ixLastData){
    camera.setPosition(1080, -2900, 570);
    camera.setFocalPoint(625,-30,-140);
    camera.setViewUp(0.0733323, 0.29837302, 0.951628);
  }
  camera.setClippingRange( [1000,5000] );
  g_renderWindow.render();
}

function setTimeStageString(ix) {
  const tHours = 200 + ix;
  tString = `${tHours} (hours), E${Math.floor(tHours / 24.0)}:${Math.floor(tHours % 24.0)}`;

  const tsElement = document.getElementById("timeStage");
  while( tsElement.firstChild ) {
    tsElement.removeChild( tsElement.firstChild );
  }
  tsElement.appendChild(document.createTextNode(tString));
}


function setCurrentStage(eValue) {
  const reader = readers[eValue];
  drawWithReader(reader, eValue);
  setTimeStageString(eValue);
}

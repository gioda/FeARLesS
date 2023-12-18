
const ixFirstData1 = 49;
const ixLastData1 = 90;

const readers1 = {};

var g_renderer1;
var g_renderWindow1;
var g_mapper1;
var g_actor1;

function initialise1() {

  const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
  const renderer = vtk.Rendering.Core.vtkRenderer.newInstance({ background: [0.2, 0.3, 0.4] });
  renderWindow.addRenderer(renderer);

  const openglRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
  renderWindow.addView(openglRenderWindow);

  const container = document.getElementById('vtkcanvas1');
  openglRenderWindow.setContainer(container);
  const { width, height } = container.getBoundingClientRect();
  openglRenderWindow.setSize(width, height);

  const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
  interactor.setView(openglRenderWindow);
  interactor.initialize();
  interactor.bindEvents(container);
  isty = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
  interactor.setInteractorStyle(isty);

  g_renderer1 = renderer;
  g_renderWindow1 = renderWindow;

  function loadXMLData(dataIx = ixFirstData1, maxIx = ixLastData1) {
    const reader = vtk.IO.XML.vtkXMLPolyDataReader.newInstance();

    const loadText = document.getElementById("fileNumber1");
    while( loadText.firstChild ) {
      loadText.removeChild( loadText.firstChild );
    }
    loadText.appendChild(document.createTextNode(`${dataIx - ixFirstData1 + 1} of ${ixLastData1 - ixFirstData1 + 1}`));

    reader.setUrl(`data/limb-flank/out/Limb-rec_2${dataIx}.vtp`).then(() => {
      readers1[dataIx] = reader;

      if (dataIx < maxIx) {
        // Chain promise...
        // Continue loading data files in sequence until there are none remaining
        loadXMLData(dataIx + 1, maxIx);
      } else {
        const reader = readers1[ixFirstData1];

        drawWithReader1(reader, dataIx);

        const loadingIndicator1 = document.getElementById("loadingIndicator1");
        loadingIndicator1.style.display = "none";

        setTimeStageString1(ixFirstData1);

        const tsSlider = document.getElementById("timeStageSlider1");
        tsSlider.min = ixFirstData1;
        tsSlider.max = ixLastData1;
        tsSlider.value = ixFirstData1;
      }
    });
  }

  loadXMLData();
}

function drawWithReader1(reader, i) {
  const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
  const actor = vtk.Rendering.Core.vtkActor.newInstance();

  g_renderer1.removeActor(g_actor1);

  g_mapper1 = mapper;
  g_actor1 = actor;

  mapper.setInputConnection(reader.getOutputPort());
  actor.setMapper(mapper);
  // actor.getProperty().setColor(1.0, 1.0, 0.0)

  g_renderer1.addActor(actor);

  // g_renderer1.resetCamera();
  const camera = g_renderer1.getActiveCamera();
  // console.log(i)
  // console.log(camera.getPosition());
  // console.log(camera.getFocalPoint());
  // console.log(camera.getViewUp());
  // console.log(camera.getClippingRange());
  if (i==ixLastData1){
    camera.setPosition(1080, -2900, 570);
    camera.setFocalPoint(625,-30,-140);
    camera.setViewUp(0.0733323, 0.29837302, 0.951628);
  }
  camera.setClippingRange( [1000,5000] );
  g_renderWindow1.render();
}

function setTimeStageString1(ix) {
  const tHours = 200 + ix;
  tString = `${tHours} (hours), E${Math.floor(tHours / 24.0)}:${Math.floor(tHours % 24.0)}`;

  const tsElement = document.getElementById("timeStage1");
  while( tsElement.firstChild ) {
    tsElement.removeChild( tsElement.firstChild );
  }
  tsElement.appendChild(document.createTextNode(tString));
}


function setCurrentStage1(eValue) {
  const reader = readers1[eValue];
  drawWithReader1(reader, eValue);
  setTimeStageString1(eValue);
}

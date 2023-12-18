
const ixFirstData2 = 1;
const ixLastData2 = 38;

const readers2 = {};

var g_renderer2;
var g_renderWindow2;
var g_mapper2;
var g_actor2;

function initialise2() {

  const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
  const renderer = vtk.Rendering.Core.vtkRenderer.newInstance({ background: [0.2, 0.3, 0.4] });
  renderWindow.addRenderer(renderer);

  const openglRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
  renderWindow.addView(openglRenderWindow);

  const container = document.getElementById('vtkcanvas2');
  openglRenderWindow.setContainer(container);
  const { width, height } = container.getBoundingClientRect();
  openglRenderWindow.setSize(width, height);

  const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
  interactor.setView(openglRenderWindow);
  interactor.initialize();
  interactor.bindEvents(container);
  isty = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
  interactor.setInteractorStyle(isty);

  g_renderer2 = renderer;
  g_renderWindow2 = renderWindow;

  function loadXMLData(dataIx = ixFirstData2, maxIx = ixLastData2) {
    const reader = vtk.IO.XML.vtkXMLPolyDataReader.newInstance();

    const loadText = document.getElementById("fileNumber2");
    while( loadText.firstChild ) {
      loadText.removeChild( loadText.firstChild );
    }
    loadText.appendChild(document.createTextNode(`${dataIx - ixFirstData2 + 1} of ${ixLastData2 - ixFirstData2 + 1}`));

    reader.setUrl(`data/heart/out/File${dataIx}.vtp`).then(() => {
      readers2[dataIx] = reader;

      if (dataIx < maxIx) {
        // Chain promise...
        // Continue loading data files in sequence until there are none remaining
        loadXMLData(dataIx + 1, maxIx);
      } else {
        const reader = readers2[ixFirstData2];

        drawWithReader2(reader, dataIx);

        const loadingIndicator2 = document.getElementById("loadingIndicator2");
        loadingIndicator2.style.display = "none";

        setTimeStageString2(ixFirstData2);

        const tsSlider = document.getElementById("timeStageSlider2");
        tsSlider.min = ixFirstData2;
        tsSlider.max = ixLastData2;
        tsSlider.value = ixFirstData2;
      }
    });
  }

  loadXMLData();
}

function drawWithReader2(reader, i) {
  const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
  const actor = vtk.Rendering.Core.vtkActor.newInstance();

  g_renderer2.removeActor(g_actor2);

  g_mapper2 = mapper;
  g_actor2 = actor;

  mapper.setInputConnection(reader.getOutputPort());
  actor.setMapper(mapper);
  // actor.getProperty().setColor(1.0, 0.0, 0.0);

  g_renderer2.addActor(actor);

  // g_renderer2.resetCamera();
  const camera = g_renderer2.getActiveCamera();
  // console.log(i)
  // console.log(camera.getPosition());
  // console.log(camera.getFocalPoint());
  // console.log(camera.getViewUp());
  // console.log(camera.getClippingRange());
  if (i==ixLastData2){
    camera.setPosition(275.683, 121.648, 40.551);
    camera.setFocalPoint(3.722, -2.883, 1.712);
    camera.setViewUp(-0.428, 0.896, 0.123);
  }
  camera.setClippingRange( [169.088, 469.195] );
  g_renderWindow2.render();
}

function setTimeStageString2(ix) {
  const tHours = (28.5-10)*(ix - 1)/37+10;
  // tString = `${tHours} (somites), E${Math.floor(tHours / 24.0)}:${Math.floor(tHours % 24.0)}`;
  tString = `somites: ${tHours}`;

  const tsElement = document.getElementById("timeStage2");
  while( tsElement.firstChild ) {
    tsElement.removeChild( tsElement.firstChild );
  }
  tsElement.appendChild(document.createTextNode(tString));
}


function setCurrentStage2(eValue) {
  const reader = readers2[eValue];
  drawWithReader2(reader, eValue);
  setTimeStageString2(eValue);
}

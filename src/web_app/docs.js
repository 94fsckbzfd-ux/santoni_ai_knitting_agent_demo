const confirmedList = document.querySelector("#confirmedList");
const uncertainList = document.querySelector("#uncertainList");
const implementedFeatureList = document.querySelector("#implementedFeatureList");
const plannedFeatureList = document.querySelector("#plannedFeatureList");
const designerStateFlow = document.querySelector("#designerStateFlow");
const serviceStateFlow = document.querySelector("#serviceStateFlow");
const athenaMvpStateFlow = document.querySelector("#athenaMvpStateFlow");
const productionOperationsStateFlow = document.querySelector("#productionOperationsStateFlow");
const hermesIntegrationStateFlow = document.querySelector("#hermesIntegrationStateFlow");
const trainingAutomationStateFlow = document.querySelector("#trainingAutomationStateFlow");
const serviceCaseStructureList = document.querySelector("#serviceCaseStructureList");
const nextDecisionList = document.querySelector("#nextDecisionList");
const docsVersion = document.querySelector("#docsVersion");

function addListItems(target, items) {
  target.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    target.append(li);
  });
}

function addFeatureItems(target, items) {
  target.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    const status = item.status ? `[${item.status}] ` : "";
    li.textContent = `${status}${item.name}: ${item.description}`;
    target.append(li);
  });
}

async function loadDocs() {
  const response = await fetch(`/api/project-docs?ts=${Date.now()}`);
  const docs = await response.json();
  if (docsVersion) docsVersion.textContent = docs.version || "";

  addFeatureItems(implementedFeatureList, docs.implemented_features || []);
  addFeatureItems(plannedFeatureList, docs.planned_features || []);
  addListItems(confirmedList, docs.confirmed || []);
  addListItems(uncertainList, docs.uncertain || []);
  addListItems(serviceCaseStructureList, docs.service_case_mock_structure || []);
  addListItems(nextDecisionList, docs.next_decisions || []);

  renderStateFlow(designerStateFlow, docs.designer_state_flow || []);
  renderStateFlow(serviceStateFlow, docs.service_state_flow || []);
  renderStateFlow(athenaMvpStateFlow, docs.athena_mvp_state_flow || []);
  renderStateFlow(productionOperationsStateFlow, docs.production_operations_state_flow || []);
  renderStateFlow(hermesIntegrationStateFlow, docs.hermes_integration_state_flow || []);
  renderStateFlow(trainingAutomationStateFlow, docs.training_automation_state_flow || []);
}

function renderStateFlow(target, stages) {
  target.innerHTML = "";
  stages.forEach((stage, index) => {
    const card = document.createElement("article");
    card.className = "doc-stage";
    card.innerHTML = `
      <div class="version-entry-header">
        <h3>${index + 1}. ${stage.stage}</h3>
        <span>${stage.status}</span>
      </div>
      <p>${stage.description}</p>
      <p><strong>Certainty:</strong> ${stage.certainty}</p>
    `;
    target.append(card);
  });
}

loadDocs().catch(() => {
  confirmedList.innerHTML = "<li>Project docs unavailable. Please restart the demo server.</li>";
});

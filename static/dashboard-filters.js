const historyRows = [...document.querySelectorAll("[data-transaction-row]")];
const searchInput = document.getElementById("history-search");
const typeFilter = document.getElementById("history-type-filter");
const categoryFilter = document.getElementById("history-category-filter");
const resultCount = document.getElementById("history-result-count");
const noResultsMessage = document.getElementById("history-no-results");

function filterTransactions() {
    const searchTerm = searchInput.value.trim().toLocaleLowerCase();
    const selectedType = typeFilter.value;
    const selectedCategory = categoryFilter.value;
    let visibleCount = 0;

    for (const row of historyRows) {
        const matchesSearch = row.textContent.toLocaleLowerCase().includes(searchTerm);
        const matchesType = !selectedType || row.dataset.type === selectedType;
        const matchesCategory = !selectedCategory || row.dataset.category === selectedCategory;
        const isVisible = matchesSearch && matchesType && matchesCategory;

        row.hidden = !isVisible;
        visibleCount += Number(isVisible);
    }

    resultCount.textContent = `Showing ${visibleCount} of ${historyRows.length} transactions`;
    noResultsMessage.hidden = visibleCount > 0;
}

if (historyRows.length > 0) {
    searchInput.addEventListener("input", filterTransactions);
    typeFilter.addEventListener("change", filterTransactions);
    categoryFilter.addEventListener("change", filterTransactions);
    filterTransactions();
}
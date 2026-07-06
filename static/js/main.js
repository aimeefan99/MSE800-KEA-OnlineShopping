document.addEventListener("DOMContentLoaded", function () {
    const AI_DRAFT_LOADING_MESSAGE = "Generating draft from your image...";
    const AI_DRAFT_SUCCESS_MESSAGE =
        "Draft generated from your image. Please review the details before publishing.";
    const AI_DRAFT_LOW_CONFIDENCE_MESSAGE =
        "The uploaded image was unclear, so the generated draft may be inaccurate. Please review the details carefully.";
    const AI_DRAFT_FAILURE_MESSAGE =
        "We could not generate a draft from this image. Please fill in the listing details manually.";

    const createListingForm = document.getElementById("create-listing-form");
    if (!createListingForm) {
        return;
    }

    const imageInput = document.getElementById("image");
    const titleInput = document.getElementById("title");
    const categorySelect = document.getElementById("category_id");
    const descriptionInput = document.getElementById("description");
    const statusMessage = document.getElementById("ai-draft-status");
    const detailsPanel = document.getElementById("ai-draft-details");
    const visibleTextValue = document.getElementById("ai-visible-text");
    const detectedAttributesValue = document.getElementById("ai-detected-attributes");
    const draftEndpoint = createListingForm.dataset.aiDraftEndpoint;
    let activeRequestId = 0;

    if (!imageInput || !titleInput || !categorySelect || !descriptionInput || !statusMessage) {
        return;
    }

    imageInput.addEventListener("change", async function () {
        const selectedFile = imageInput.files && imageInput.files[0];
        if (!selectedFile) {
            return;
        }

        // Ignore stale AI responses when the user quickly chooses another image.
        activeRequestId += 1;
        const requestId = activeRequestId;
        setStatus(AI_DRAFT_LOADING_MESSAGE, "alert alert-info");
        hideDraftDetails();

        const formData = new FormData();
        formData.append("image", selectedFile);

        try {
            const response = await fetch(draftEndpoint, {
                method: "POST",
                body: formData,
            });
            const payload = await response.json();
            if (requestId !== activeRequestId) {
                return;
            }

            if (!response.ok || !payload.success) {
                setStatus(
                    payload.error || AI_DRAFT_FAILURE_MESSAGE,
                    "alert alert-warning"
                );
                return;
            }

            fillDraftFields(payload.draft);
            renderDraftDetails(payload.draft);

            if (payload.draft.confidence === "low") {
                setStatus(AI_DRAFT_LOW_CONFIDENCE_MESSAGE, "alert alert-warning");
            } else {
                setStatus(AI_DRAFT_SUCCESS_MESSAGE, "alert alert-success");
            }
        } catch (_error) {
            if (requestId !== activeRequestId) {
                return;
            }
            setStatus(AI_DRAFT_FAILURE_MESSAGE, "alert alert-warning");
        }
    });

    function fillDraftFields(draft) {
        titleInput.value = draft.suggested_title || "";
        descriptionInput.value = draft.suggested_description || "";
        selectCategoryByName(draft.suggested_category || "");
    }

    function selectCategoryByName(categoryName) {
        const normalizedCategoryName = categoryName.trim().toLowerCase();
        const matchingOption = Array.from(categorySelect.options).find(function (option) {
            return option.text.trim().toLowerCase() === normalizedCategoryName;
        });
        if (matchingOption) {
            categorySelect.value = matchingOption.value;
        }
    }

    function renderDraftDetails(draft) {
        visibleTextValue.textContent = draft.visible_text.length
            ? draft.visible_text.join(", ")
            : "-";
        detectedAttributesValue.textContent = draft.detected_attributes.length
            ? draft.detected_attributes.join(", ")
            : "-";
        detailsPanel.classList.remove("d-none");
    }

    function hideDraftDetails() {
        if (detailsPanel) {
            detailsPanel.classList.add("d-none");
        }
    }

    function setStatus(message, className) {
        statusMessage.textContent = message;
        statusMessage.className = className;
    }
});

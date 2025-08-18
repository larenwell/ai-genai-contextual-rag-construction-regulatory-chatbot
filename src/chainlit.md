# Asistente de Normativa

Bienvenido al asistente especializado en normativas técnicas y documentos de ingeniería.

<style>
/* Improve typography and spacing */
.cl-message {
    line-height: 1.5;
}

.cl-message h3 {
    font-size: 1.2em !important;
    margin-bottom: 0.5em !important;
    margin-top: 1em !important;
}

.cl-message h4 {
    font-size: 1.1em !important;
    margin-bottom: 0.4em !important;
    margin-top: 0.8em !important;
}

.cl-message p {
    margin-bottom: 0.8em !important;
}

/* Consistent bullet list spacing */
.cl-message ul {
    margin-bottom: 0.8em !important;
    margin-top: 0.2em !important;
}

.cl-message li {
    margin-bottom: 0.4em !important;
    margin-top: 0 !important;
    padding-left: 0.5em !important;
    line-height: 1.4 !important;
}

/* Remove extra spacing after last list item */
.cl-message li:last-child {
    margin-bottom: 0 !important;
}

/* Compact sources display */
.cl-message .sources-section {
    font-size: 0.9em !important;
    line-height: 1.4 !important;
}

/* Ensure consistent paragraph spacing */
.cl-message p + ul {
    margin-top: 0.2em !important;
}

.cl-message ul + p {
    margin-top: 0.5em !important;
}

/* Reduce spacing for References section specifically */
.cl-message h3 + ul,
.cl-message h4 + ul {
    margin-top: 0.1em !important;
}

/* Sources section styling */
.cl-message h3:contains("Fuentes consultadas") + div,
.cl-message h3:contains("Fuentes consultadas") ~ div {
    margin-top: 0.3em !important;
}

/* Ensure sources have consistent line spacing */
.cl-message .sources-content {
    line-height: 1.6 !important;
}

/* Better spacing for numbered lists */
.cl-message ol {
    margin-top: 0.2em !important;
    margin-bottom: 0.8em !important;
}

.cl-message ol li {
    margin-bottom: 0.3em !important;
    padding-left: 0.3em !important;
}

/* Sources section specific spacing */
.cl-message h3:contains("Fuentes consultadas") {
    margin-bottom: 0.3em !important;
}

/* Sources list container spacing */
.cl-message .sources-list {
    margin-top: 0.2em !important;
    margin-bottom: 0.6em !important;
}

/* Ensure proper spacing after sources before next section */
.cl-message .sources-section + div {
    margin-top: 0.4em !important;
}

/* Target sources heading specifically */
.cl-message h3:contains("Fuentes consultadas") {
    margin-bottom: 0.3em !important;
}

/* Sources list spacing */
.cl-message div.sources-list {
    margin-top: 0.2em !important;
    margin-bottom: 0.5em !important;
}

/* Spacing after sources list */
.cl-message div.sources-list + div {
    margin-top: 0.4em !important;
}

/* Sources list items spacing */
.cl-message div.sources-list {
    line-height: 1.5 !important;
}

.cl-message div.sources-list > * {
    margin-bottom: 0.2em !important;
}

.cl-message div.sources-list > *:last-child {
    margin-bottom: 0 !important;
}

/* Ensure consistent spacing with other sections */
.cl-message h3 + div.sources-list {
    margin-top: 0.2em !important;
}

/* Target the rendered markdown sources list */
.cl-message h3:contains("Fuentes consultadas") + p,
.cl-message h3:contains("Fuentes consultadas") ~ p {
    margin-top: 0.1em !important;
    margin-bottom: 0.1em !important;
    line-height: 1.3 !important;
    font-size: 0.95em !important;
}

/* Ensure proper spacing after the sources list */
.cl-message h3:contains("Fuentes consultadas") ~ p:last-of-type {
    margin-bottom: 0.3em !important;
}

/* Target numbered list items specifically */
.cl-message p:contains("1."),
.cl-message p:contains("2."),
.cl-message p:contains("3."),
.cl-message p:contains("4."),
.cl-message p:contains("5.") {
    margin-bottom: 0.1em !important;
    margin-top: 0 !important;
    padding-left: 0.2em !important;
}

/* Ensure consistent font sizing for sources */
.cl-message h3:contains("Fuentes consultadas") ~ p {
    font-size: 0.95em !important;
    line-height: 1.3 !important;
}

/* Better spacing for the entire sources section */
.cl-message h3:contains("Fuentes consultadas") {
    margin-bottom: 0.15em !important;
}

/* Compact spacing between source items */
.cl-message h3:contains("Fuentes consultadas") ~ p:not(:last-of-type) {
    margin-bottom: 0.1em !important;
}

/* Proper spacing after the last source item */
.cl-message h3:contains("Fuentes consultadas") ~ p:last-of-type {
    margin-bottom: 0.3em !important;
}

/* Ensure inline code styling for filenames */
.cl-message h3:contains("Fuentes consultadas") ~ p code {
    background-color: rgba(255, 255, 255, 0.1) !important;
    padding: 0.1em 0.3em !important;
    border-radius: 0.2em !important;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
    font-size: 0.9em !important;
}
</style>

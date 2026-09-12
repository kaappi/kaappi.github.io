// Shared CodeMirror 6 editor factory for the playground and tour.
//
// Loads the vendored bundle relative to this module, applies the Kaappi
// "Dark Roast" highlight palette, wires Ctrl/Cmd+Enter to onRun, and falls
// back to a plain textarea if the bundle fails to load. Returns a small
// handle: { getContent, setContent, destroy } — identical shape for both
// the CodeMirror and textarea paths, so callers never branch on which is live.

export async function createSchemeEditor({ parent, doc, isDark, onRun }) {
  const runOnChord = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      onRun();
    }
  };

  try {
    const { EditorView, EditorState, basicSetup, StreamLanguage, HighlightStyle,
            syntaxHighlighting, tags, scheme } =
      await import("./codemirror-bundle.mjs");

    const darkHighlight = HighlightStyle.define([
      { tag: [tags.keyword, tags.standard(tags.variableName)], color: "#E8B563" },
      { tag: tags.comment, color: "#9C8A77", fontStyle: "italic" },
      { tag: tags.string, color: "#BFD08A" },
      { tag: tags.number, color: "#E0A867" },
      { tag: tags.atom, color: "#E8B563" },
      { tag: [tags.variableName, tags.definition(tags.variableName)], color: "#4FC4B2" },
      { tag: tags.bracket, color: "#BBA890" },
      { tag: [tags.meta, tags.operator], color: "#D08B3C" },
    ]);

    const lightHighlight = HighlightStyle.define([
      { tag: [tags.keyword, tags.standard(tags.variableName)], color: "#9A6A1E" },
      { tag: tags.comment, color: "#9C8A77", fontStyle: "italic" },
      { tag: tags.string, color: "#5A7A22" },
      { tag: tags.number, color: "#9A6A1E" },
      { tag: tags.atom, color: "#9A6A1E" },
      { tag: [tags.variableName, tags.definition(tags.variableName)], color: "#1E8A7A" },
      { tag: tags.bracket, color: "#8A7A6A" },
      { tag: [tags.meta, tags.operator], color: "#A06A20" },
    ]);

    const theme = EditorView.theme({
      "&": { backgroundColor: "transparent" },
      ".cm-content": { caretColor: isDark ? "#F3E9DB" : "#1A1410" },
    }, { dark: isDark });

    const view = new EditorView({
      state: EditorState.create({
        doc,
        extensions: [
          basicSetup,
          theme,
          syntaxHighlighting(isDark ? darkHighlight : lightHighlight),
          EditorView.domEventHandlers({ keydown: runOnChord }),
          StreamLanguage.define(scheme),
        ],
      }),
      parent,
    });

    return {
      getContent: () => view.state.doc.toString(),
      setContent: (code) => view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: code },
      }),
      destroy: () => view.destroy(),
    };
  } catch (e) {
    console.warn("CodeMirror failed to load; using plain textarea.", e);
    const ta = document.createElement("textarea");
    ta.value = doc;
    ta.spellcheck = false;
    Object.assign(ta.style, {
      width: "100%", height: "100%", resize: "none", background: "transparent",
      color: "inherit", border: "none", outline: "none", padding: ".75rem",
      fontFamily: "var(--kp-mono)", fontSize: ".85rem", lineHeight: "1.5", tabSize: 2,
    });
    ta.addEventListener("keydown", runOnChord);
    parent.appendChild(ta);

    return {
      getContent: () => ta.value,
      setContent: (code) => { ta.value = code; },
      destroy: () => ta.remove(),
    };
  }
}

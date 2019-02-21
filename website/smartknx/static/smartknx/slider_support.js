
function create_slider(element) {
    let slider = new Slider(element, { rangeHighlights: [{ "start": 0, "end": 43 }] });

    return slider;
}


function change_rangeHighlights(slider, position) {
    slider.setAttribute("rangeHighlights", [{ "start": 0, "end": position }]);

    if (slider.rangeHighlightElements.length > 0 && Array.isArray(slider.options.rangeHighlights) && slider.options.rangeHighlights.length > 0) {
        for (let i = 0; i < slider.options.rangeHighlights.length; i++) {
            var startPercent = slider._toPercentage(slider.options.rangeHighlights[i].start);
            var endPercent = slider._toPercentage(slider.options.rangeHighlights[i].end);

            if (slider.options.reversed) {
                var sp = 100 - endPercent;
                endPercent = 100 - startPercent;
                startPercent = sp;
            }

            var currentRange = slider._createHighlightRange(startPercent, endPercent);

            if (currentRange) {
                if (slider.options.orientation === 'vertical') {
                    slider.rangeHighlightElements[i].style.top = `${currentRange.start}%`;
                    slider.rangeHighlightElements[i].style.height = `${currentRange.size}%`;
                } else {
                    if (slider.options.rtl) {
                        slider.rangeHighlightElements[i].style.right = `${currentRange.start}%`;
                    } else {
                        slider.rangeHighlightElements[i].style.left = `${currentRange.start}%`;
                    }
                    slider.rangeHighlightElements[i].style.width = `${currentRange.size}%`;
                }
            } else {
                slider.rangeHighlightElements[i].style.display = "none";
            }
        }
    }
}
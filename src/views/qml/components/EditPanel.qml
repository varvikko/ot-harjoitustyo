import QtQuick 2.12
import QtQuick.Controls 2.12

ScrollView {
    property var source
    property var resource_id
    id: scrollView
    clip: true
    height: parent ? parent.height : 0

    TextEdit {
        objectName: 'editTemplateDialogContent'
        id: editTemplateDialogContent
        color: '#666666'
        text: source
        anchors.fill: parent
        font.pixelSize: 12
        wrapMode: Text.WrapAnywhere
        selectionColor: '#9b9b9b'
        font.family: 'Source Code Pro'
        padding: 25
        selectByMouse: true
    }
}
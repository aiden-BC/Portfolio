using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
public class DoorTrigger : MonoBehaviour
{
    public Animator anim;
    public void OnActivated(ActivateEventArgs arg0)
    {
        anim.SetTrigger("Click");
    }
}

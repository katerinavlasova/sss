#include <linux/init.h>
#include <linux/module.h>
#include <linux/usb.h>
#include <linux/kernel.h>
#include <linux/list.h>
#include <linux/slab.h>
#include <asm/segment.h>
#include <linux/syscalls.h>
#include <linux/notifier.h>
#include "config.h"

#define USB_COUNT 4
#define NAME_USB_LEN 8

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Vlasova");


typedef struct our_usb_device {
    struct usb_device_id dev_id;
    enum usb_device_speed speed;
    char *product;
    char *manufacturer;
    char *serial;
    // This is used to link nodes together in the list.
    struct list_head list_node;
} our_usb_device_t;

// Declare and init the head node of the linked list.
LIST_HEAD(connected_devices);

// Match device with device id.
static bool device_match_device_id(struct usb_device *dev, const struct usb_device_id *dev_id)
{
    // Check idVendor and idProduct, which are used.
    if (dev_id->idVendor != dev->descriptor.idVendor)
        return false;
    if (dev_id->idProduct != dev->descriptor.idProduct)
        return false;
    return true;
}

// Match device id with device id.
static bool device_id_match_device_id(struct usb_device_id *new_dev_id, const struct usb_device_id *dev_id)
{
    // Check idVendor and idProduct, which are used.
    if (dev_id->idVendor != new_dev_id->idVendor)
        return false;
    if (dev_id->idProduct != new_dev_id->idProduct)
        return false;
    return true;
}

// Check our list of devices, if we know device.
static char *usb_device_id_is_known(struct usb_device_id *dev)
{
    unsigned long known_devices_len = sizeof(known_devices) / sizeof(known_devices[0]);
    int i = 0;
    for (i = 0; i < known_devices_len; i++)
    {
        if (device_id_match_device_id(dev, &known_devices[i].dev_id))
        {
            int size = sizeof(known_devices[i].name);
            char *name = (char *)kmalloc(size + 1, GFP_KERNEL);
            int j = 0;
            for (j = 0; j < size; j++)
                name[j] = known_devices[i].name[j];
            name[size + 1] = '\0';

            return name;
        }
    }
    return NULL;
}

static char *knowing_device(void)
{
    our_usb_device_t *temp;
    int count = 0;
    char *name;

    list_for_each_entry(temp, &connected_devices, list_node) {
        name = usb_device_id_is_known(&temp->dev_id);
        if (!name)
            return NULL;
        count++;
    }
    if (0 == count)
        return NULL;
    return name;
}

static void print_our_usb_devices(void)
{
    our_usb_device_t *temp;
    int count = 0;
    char s[] = " H";
    list_for_each_entry(temp, &connected_devices, list_node) {
        printk(KERN_INFO "USB MODULE CURRENT DEVICE: Node %d ID = (%x:%x), Product = %s, Manufacturer = %s, Speed = %d Mbps, serial = %s. \n", count++, temp->dev_id.idVendor, temp->dev_id.idProduct, temp->product, temp->manufacturer, temp->speed, temp->serial);
    }
}

static void add_our_usb_device(struct usb_device *dev)
{
    our_usb_device_t* new_usb_device = (our_usb_device_t *)kmalloc(sizeof(our_usb_device_t), GFP_KERNEL);
    struct usb_device_id new_id = { USB_DEVICE(dev->descriptor.idVendor, dev->descriptor.idProduct) };
    new_usb_device->dev_id = new_id;
    new_usb_device->product = dev->product;
    new_usb_device->manufacturer = dev->manufacturer;
    new_usb_device->speed = dev->speed;
    new_usb_device->serial = dev->serial;
    list_add_tail(&new_usb_device->list_node, &connected_devices);
}

static void delete_our_usb_device(struct usb_device *dev)
{
    our_usb_device_t *device, *temp;
    list_for_each_entry_safe(device, temp, &connected_devices, list_node) 
    {
        if (device_match_device_id(dev, &device->dev_id))
        {
            list_del(&device->list_node);
            kfree(device);
        }
    }
}

// If usb device inserted.
static void usb_dev_insert(struct usb_device *dev)
{   
    add_our_usb_device(dev);
    char *name = knowing_device();
    
    if (name)
        printk(KERN_INFO "USB MODULE: New device: (%04X:%04X), Product: %s, Manufacturer: %s, Speed: %d Mbps, Serial: %s.\n", dev->descriptor.idVendor, dev->descriptor.idProduct, dev->product, dev->manufacturer, dev->speed, dev->serial);
}

// If usb device removed.
static void usb_dev_remove(struct usb_device *dev)
{
    delete_our_usb_device(dev);
    char *name = knowing_device();

    if (!name)
        printk(KERN_INFO "USB MODULE: Deleted device (%04X:%04X), Product: %s, Manufacturer: %s, Speed: %d Mbps, Serial: %s.\n", dev->descriptor.idVendor, dev->descriptor.idProduct, dev->product, dev->manufacturer, dev->speed, dev->serial);
}

// New notify.
static int notify(struct notifier_block *self, unsigned long action, void *dev)
{
    // Events, which our notifier react.
    switch (action) 
    {
        case USB_DEVICE_ADD:
            usb_dev_insert(dev);
	        break;
        case USB_DEVICE_REMOVE:
            usb_dev_remove(dev);
	        break;
        default:
	        break;
    }
    return 0;
}

// Struct to react on different notifies.
static struct notifier_block usb_notify = {
    .notifier_call = notify,
};

static int __init my_module_init(void)
{
    usb_register_notify(&usb_notify);
    printk(KERN_INFO "USB MODULE: loaded.\n");
    return 0;
}

static void __exit my_module_exit(void)
{
    usb_unregister_notify(&usb_notify);    
    printk(KERN_INFO "USB MODULE: unloaded.\n");
}

module_init(my_module_init);
module_exit(my_module_exit);
